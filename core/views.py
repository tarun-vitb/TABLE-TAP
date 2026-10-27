from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import io
from .models import Restaurant, Table, Category, MenuItem, Order, OrderItem
from .forms import RestaurantForm, CategoryForm, MenuItemForm, TableForm

def home(request):
    return render(request, "core/home.html", {"restaurants": Restaurant.objects.all()[:12]})

def _cart(request, restaurant):
    return request.session.get(f"cart_{restaurant.id}", {})

def _save_cart(request, restaurant, cart):
    request.session[f"cart_{restaurant.id}"] = cart
    request.session.modified = True

def public_menu(request, slug):
    r = get_object_or_404(Restaurant, slug=slug)
    table = None
    code = request.GET.get("table")
    if code: table = Table.objects.filter(restaurant=r, code=code).first()
    if request.method == "POST":
        cart = _cart(request, r)
        item_id = request.POST.get("item_id"); action = request.POST.get("action")
        if item_id:
            if action == "add": cart[item_id] = cart.get(item_id, 0) + 1
            elif action == "remove":
                cart[item_id] = cart.get(item_id, 0) - 1
                if cart[item_id] <= 0: cart.pop(item_id, None)
            _save_cart(request, r, cart)
        return redirect(f"/r/{slug}/?table={code}" if code else f"/r/{slug}/")
    categories = r.categories.prefetch_related("items").all()
    cart = _cart(request, r)
    return render(request, "core/public_menu.html", {"r": r, "table": table, "categories": categories, "cart": cart})

def cart_view(request, slug):
    r = get_object_or_404(Restaurant, slug=slug)
    table = None; code = request.GET.get("table")
    if code: table = Table.objects.filter(restaurant=r, code=code).first()
    cart = _cart(request, r)
    items = []; subtotal = Decimal("0")
    for item_id, qty in cart.items():
        try: item = MenuItem.objects.get(id=item_id, restaurant=r)
        except MenuItem.DoesNotExist: continue
        items.append((item, qty, item.price * qty)); subtotal += item.price * qty
    if request.method == "POST" and items:
        order = Order.objects.create(restaurant=r, table=table, note=request.POST.get("note","")[:300])
        for item, qty, _ in items:
            OrderItem.objects.create(order=order, menu_item=item, quantity=qty, unit_price=item.price)
        _save_cart(request, r, {})
        return redirect(f"/r/{slug}/track/{order.id}/")
    gst = round(float(subtotal) * 0.05, 2)
    return render(request, "core/cart.html", {"r": r, "table": table, "items": items, "subtotal": subtotal, "gst": gst, "total": round(float(subtotal)+gst, 2)})

def track_order(request, slug):
    r = get_object_or_404(Restaurant, slug=slug)
    # order_id is in URL kwargs via track view wrapper below; handled in urls by passing? See track_order_by_id
    return redirect(f"/r/{slug}/")

def track_order_by_id(request, slug, order_id):
    r = get_object_or_404(Restaurant, slug=slug)
    order = get_object_or_404(Order, id=order_id, restaurant=r)
    return render(request, "core/track.html", {"r": r, "order": order})

# Patch: urls track route calls track_order_by_id via alias
track_order = track_order_by_id

@login_required
def dashboard(request):
    return render(request, "core/dashboard.html", {"restaurants": request.user.restaurants.all()})

@login_required
def restaurant_new(request):
    if request.method == "POST":
        form = RestaurantForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False); obj.owner = request.user; obj.save()
            messages.success(request, "Restaurant created. Now add categories, items and tables.")
            return redirect("menu_manage", slug=obj.slug)
    else: form = RestaurantForm()
    return render(request, "core/form.html", {"form": form, "title": "New restaurant"})

def _owned(request, slug):
    return get_object_or_404(Restaurant, slug=slug, owner=request.user)

@login_required
def restaurant_dashboard(request, slug):
    r = _owned(request, slug)
    today = timezone.now().date()
    orders = r.orders.filter(created_at__date=today).order_by("-created_at")
    paid = orders.filter(is_paid=True)
    sales = sum(o.total for o in paid)
    return render(request, "core/restaurant_dashboard.html", {"r": r, "orders": orders, "sales": round(sales,2), "count": orders.count()})

@login_required
def menu_manage(request, slug):
    r = _owned(request, slug)
    if request.method == "POST":
        if "category" in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False); obj.restaurant = r; obj.save(); return redirect("menu_manage", slug=slug)
        elif "toggle" in request.POST:
            item = get_object_or_404(MenuItem, id=request.POST.get("toggle"), restaurant=r)
            item.is_available = not item.is_available; item.save(); return redirect("menu_manage", slug=slug)
        else:
            form = MenuItemForm(request.POST, restaurant=r)
            if form.is_valid():
                obj = form.save(commit=False); obj.restaurant = r; obj.save(); return redirect("menu_manage", slug=slug)
    return render(request, "core/menu_manage.html", {"r": r, "cat_form": CategoryForm(), "item_form": MenuItemForm(restaurant=r)})

@login_required
def tables_manage(request, slug):
    r = _owned(request, slug)
    if request.method == "POST":
        form = TableForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False); obj.restaurant = r; obj.save(); return redirect("tables_manage", slug=slug)
    return render(request, "core/tables.html", {"r": r, "form": TableForm()})

@login_required
def kds(request, slug):
    r = _owned(request, slug)
    if request.method == "POST":
        order = get_object_or_404(Order, id=request.POST.get("order_id"), restaurant=r)
        new = request.POST.get("status")
        if new in dict(Order.STATUS): order.status = new; order.save()
        return redirect("kds", slug=slug)
    active = r.orders.exclude(status__in=["served","billed","cancelled"]).order_by("created_at")
    done = r.orders.filter(status__in=["served","billed"]).order_by("-created_at")[:10]
    return render(request, "core/kds.html", {"r": r, "active": active, "done": done})

@login_required
def order_detail(request, slug, order_id):
    r = _owned(request, slug)
    order = get_object_or_404(Order, id=order_id, restaurant=r)
    if request.method == "POST":
        if "pay" in request.POST:
            order.payment_mode = request.POST.get("payment_mode","cash"); order.is_paid = True; order.status = "billed"; order.save()
        elif "status" in request.POST:
            order.status = request.POST.get("status"); order.save()
        return redirect("order_detail", slug=slug, order_id=order.id)
    return render(request, "core/order_detail.html", {"r": r, "order": order})

@login_required
def table_qr(request, slug, table_id):
    r = _owned(request, slug)
    table = get_object_or_404(Table, id=table_id, restaurant=r)
    url = request.build_absolute_uri(f"/r/{r.slug}/?table={table.code}")
    try:
        import qrcode
        img = qrcode.make(url)
        buf = io.BytesIO(); img.save(buf, format="PNG")
        return HttpResponse(buf.getvalue(), content_type="image/png")
    except Exception:
        return HttpResponse(f"QR URL: {url}", content_type="text/plain")
