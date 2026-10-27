from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import secrets

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurants")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, default="Bhimavaram")
    phone = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=100, blank=True, help_text="Restaurant's own UPI ID for UPI payments. We never hold customer money.")
    plan = models.CharField(max_length=20, default="Growth", choices=[("Starter","Starter"),("Growth","Growth"),("Scale","Scale")])
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "restaurant"
            slug, i = base, 2
            while Restaurant.objects.filter(slug=slug).exists():
                slug, i = f"{base}-{i}", i + 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self): return self.name

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")
    number = models.CharField(max_length=20)
    code = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if not self.code: self.code = secrets.token_hex(4)
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.restaurant.name} - Table {self.number}"

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    class Meta: ordering = ["sort_order", "name"]
    def __str__(self): return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    def __str__(self): return self.name

class Order(models.Model):
    STATUS = [("placed","Placed"),("accepted","Accepted"),("preparing","Preparing"),("ready","Ready"),("served","Served"),("billed","Billed"),("cancelled","Cancelled")]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="placed")
    note = models.CharField(max_length=300, blank=True)
    payment_mode = models.CharField(max_length=20, blank=True, choices=[("cash","Cash"),("upi","UPI")])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def subtotal(self): return sum(i.line_total for i in self.items.all())
    @property
    def gst(self): return round(float(self.subtotal) * 0.05, 2)
    @property
    def total(self): return round(float(self.subtotal) + self.gst, 2)
    def __str__(self): return f"Order #{self.id} - {self.restaurant.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    @property
    def line_total(self): return float(self.unit_price) * self.quantity
