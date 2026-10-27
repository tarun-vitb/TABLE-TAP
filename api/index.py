"""Vercel entrypoint for the TableTap Django app.

Vercel runs this file as a serverless function. On each cold start this
module runs migrate (idempotent) and seeds the demo restaurant ONLY if
no restaurant exists yet. With a shared Postgres DATABASE_URL / POSTGRES_URL
(see qrtap/settings.py) that seed runs exactly once, and every instance
shares the same data — so orders, table tokens and login sessions persist
across cold starts and instances. Without a database URL the fallback is
SQLite in /tmp, which is per-instance and NOT persistent (view-only mode).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrtap.settings")

import django

django.setup()

if os.environ.get("VERCEL"):
    try:
        from django.core.management import call_command

        call_command("migrate", run_syncdb=True, verbosity=0)
        from django.contrib.auth.models import User
        from core.models import Restaurant, Category, MenuItem, Table

        if Restaurant.objects.count() == 0:
            user, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@example.com"})
            user.set_password("owner123")
            user.is_staff = True
            user.save()
            r = Restaurant.objects.create(owner=user, name="Sri Sai Cafe", city="Bhimavaram",
                                          address="Near College Road, Bhimavaram",
                                          upi_id="srisaicafe@upi", plan="Growth")
            cats = {}
            for name in ["Starters", "Main Course", "Breads & Rice", "Beverages"]:
                cats[name] = Category.objects.create(restaurant=r, name=name)
            menu = [("Starters", "Veg Manchuria", 120, True), ("Starters", "Chicken 65", 180, False),
                    ("Main Course", "Paneer Butter Masala", 190, True), ("Main Course", "Chicken Biryani", 220, False),
                    ("Main Course", "Veg Fried Rice", 140, True), ("Breads & Rice", "Butter Naan", 40, True),
                    ("Breads & Rice", "Steamed Rice", 80, True), ("Beverages", "Filter Coffee", 30, True),
                    ("Beverages", "Sweet Lassi", 60, True)]
            for cat, name, price, veg in menu:
                MenuItem.objects.create(restaurant=r, category=cats[cat], name=name,
                                        price=price, is_veg=veg, description="Freshly prepared.")
            for n in ["1", "2", "3", "4"]:
                Table.objects.create(restaurant=r, number=n)
    except Exception:
        # Never crash the whole deployment because demo seeding failed.
        pass

from qrtap.wsgi import application

app = application
