"""Seed a demo restaurant + menu + tables. Run: python manage.py shell < seed_demo.py
Or: python seed_demo.py (it sets up Django itself)."""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrtap.settings")
django.setup()
from django.contrib.auth.models import User
from core.models import Restaurant, Category, MenuItem, Table
user, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@example.com"})
user.set_password("owner123"); user.is_staff = True; user.save()
r, _ = Restaurant.objects.get_or_create(slug="sri-sai-cafe", defaults={"owner": user, "name": "Sri Sai Cafe", "city": "Bhimavaram", "address": "Near College Road, Bhimavaram", "upi_id": "srisaicafe@upi", "plan": "Growth"})
cats = {}
for name in ["Starters", "Main Course", "Breads & Rice", "Beverages"]:
    cats[name], _ = Category.objects.get_or_create(restaurant=r, name=name)
menu = [("Starters","Veg Manchuria",120,True),("Starters","Chicken 65",180,False),("Main Course","Paneer Butter Masala",190,True),("Main Course","Chicken Biryani",220,False),("Main Course","Veg Fried Rice",140,True),("Breads & Rice","Butter Naan",40,True),("Breads & Rice","Steamed Rice",80,True),("Beverages","Filter Coffee",30,True),("Beverages","Sweet Lassi",60,True)]
for cat, name, price, veg in menu:
    MenuItem.objects.get_or_create(restaurant=r, category=cats[cat], name=name, defaults={"price": price, "is_veg": veg, "description": "Freshly prepared."})
for n in ["1","2","3","4"]:
    Table.objects.get_or_create(restaurant=r, number=n)
print("Demo ready: restaurant /r/sri-sai-cafe/  owner login: owner / owner123")
print("Tables:", [(t.number, t.code) for t in r.tables.all()])
