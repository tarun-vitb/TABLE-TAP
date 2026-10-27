from django import forms
from .models import Restaurant, Category, MenuItem, Table
class RestaurantForm(forms.ModelForm):
    class Meta: model = Restaurant; fields = ["name","address","city","phone","upi_id","plan"]
class CategoryForm(forms.ModelForm):
    class Meta: model = Category; fields = ["name","sort_order"]
class MenuItemForm(forms.ModelForm):
    class Meta: model = MenuItem; fields = ["category","name","description","price","is_veg","is_available"]
    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant: self.fields["category"].queryset = restaurant.categories.all()
class TableForm(forms.ModelForm):
    class Meta: model = Table; fields = ["number"]
