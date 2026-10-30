"""Seed a demo restaurant + menu + tables. Run: python manage.py shell < seed_demo.py
Or: python seed_demo.py (it sets up Django itself).
Demo photos: files in demo_images/ are generic web photos for the demo menu
only — they are NOT Sri Sai Cafe's own food photos. A real restaurant
replaces them by uploading its own photos from the menu page."""
import os, django
from pathlib import Path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrtap.settings")
django.setup()
from django.core.files import File
from django.contrib.auth.models import User
from core.models import Restaurant, Category, MenuItem, Table
BASE = Path(__file__).resolve().parent
user, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@example.com"})
user.set_password("owner123"); user.is_staff = True; user.save()
r, _ = Restaurant.objects.get_or_create(slug="sri-sai-cafe", defaults={"owner": user, "name": "Sri Sai Cafe", "city": "Bhimavaram", "address": "Near College Road, Bhimavaram", "upi_id": "srisaicafe@upi", "plan": "Growth"})
cats = {}
for name in ["Starters", "Main Course", "Breads & Rice", "Beverages"]:
    cats[name], _ = Category.objects.get_or_create(restaurant=r, name=name)
menu = [
    ("Starters", "Veg Manchuria", 120, True, "Crisp vegetable dumplings tossed in a spicy Indo-Chinese sauce.", "veg-manchuria.jpg"),
    ("Starters", "Chicken 65", 180, False, "Spicy, deep-fried chicken tossed with curry leaves and red chillies.", "chicken-65.jpg"),
    ("Main Course", "Paneer Butter Masala", 190, True, "Soft paneer in a rich tomato-butter gravy, served with butter naan.", "paneer-butter-masala.jpg"),
    ("Main Course", "Chicken Biryani", 220, False, "Fragrant basmati rice layered with spiced chicken and fried onions.", "chicken-biryani.jpg"),
    ("Main Course", "Veg Fried Rice", 140, True, "Wok-tossed rice with mixed vegetables and a light soy seasoning.", "veg-fried-rice.jpg"),
    ("Breads & Rice", "Butter Naan", 40, True, "Soft tandoor-baked flatbread brushed with butter.", "butter-naan.jpg"),
    ("Breads & Rice", "Steamed Rice", 80, True, "Plain steamed rice, a simple base for any curry.", "steamed-rice.jpg"),
    ("Beverages", "Filter Coffee", 30, True, "Strong South Indian filter coffee served frothy and hot.", "filter-coffee.jpg"),
    ("Beverages", "Sweet Lassi", 60, True, "Chilled sweet curd drink, lightly flavoured.", "sweet-lassi.jpg"),
]
for cat, name, price, veg, desc, photo in menu:
    item, created = MenuItem.objects.get_or_create(restaurant=r, category=cats[cat], name=name, defaults={"price": price, "is_veg": veg, "description": desc})
    if created or not item.image:
        path = BASE / "demo_images" / photo
        # Steamed rice was downloaded as a PNG; the seed accepts either.
        if not path.exists():
            alt = path.with_suffix(".png")
            path = alt if alt.exists() else path
        if path.exists():
            with open(path, "rb") as f:
                item.image.save(path.name, File(f), save=True)
for n in ["1", "2", "3", "4"]:
    Table.objects.get_or_create(restaurant=r, number=n)
print("Demo ready: restaurant /r/sri-sai-cafe/  owner login: owner / owner123")
print("Tables:", [(t.number, t.code) for t in r.tables.all()])
