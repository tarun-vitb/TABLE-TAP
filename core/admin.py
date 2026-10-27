from django.contrib import admin
from .models import Restaurant, Table, Category, MenuItem, Order, OrderItem
admin.site.register([Restaurant, Table, Category, MenuItem, Order, OrderItem])
