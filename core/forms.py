from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Restaurant, Category, MenuItem, Table
class OwnerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Used for your owner account.")
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
class RestaurantForm(forms.ModelForm):
    class Meta: model = Restaurant; fields = ["name","address","city","phone","upi_id","plan"]
class CategoryForm(forms.ModelForm):
    class Meta: model = Category; fields = ["name","sort_order"]
class MenuItemForm(forms.ModelForm):
    class Meta: model = MenuItem; fields = ["category","name","description","price","image","is_veg","is_available"]
    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant: self.fields["category"].queryset = restaurant.categories.all()
class TableForm(forms.ModelForm):
    class Meta: model = Table; fields = ["number"]
