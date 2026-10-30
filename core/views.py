from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
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
    restaurants = Restaurant.objects.all()[:12]
    demo = restaurants[0] if restaurants else None
    preview_items = demo.items.filter(is_available=True)[:3] if demo else []
    return render(request, "core/home.html", {"restaurants": restaurants, "demo": demo, "preview_items": preview_items})

def signup(request):
    from .forms import OwnerSignupForm
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = OwnerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Welcome to TableTap. Create your first restaurant to get its QR menu.")
            return redirect("dashboard")
    else:
        form = OwnerSignupForm()
    return render(request, "core/signup.html", {"form": form})

def _cart(request, restaurant):
    return request.session.get(f"cart_{restaurant.id}", {})

def _save_cart(request, restaurant, cart):
    request.session[f"cart_{restaurant.id}"] = cart
    request.session.modified = True

def _cart_totals(request, r):
    """Cart state for the customer UI: per-item qty, count, total incl. GST."""
    cart = _cart(request, r)
    qty = {}
    subtotal = Decimal("0")
    for item_id, q in cart.items():
        try: item = MenuItem.objects.get(id=item_id, restaurant=r)
        except MenuItem.DoesNotExist: continue
        qty[item.id] = q
        subtotal += item.price * q
    gst = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
    return qty, sum(qty.values()), subtotal + gst

def public_menu(request, slug):
    r = get_object_or_404(Restaurant, slug=slug)
    table = None
    code = request.GET.get("table")
    if code: table = Table.objects.filter(restaurant=r, code=code).first()
    # Search / Veg filter come from GET and are preserved across Add/Remove
    # POSTs, so adding an item never resets the customer's view.
    q = (request.GET.get("q") or "").strip()
    veg_only = request.GET.get("veg") == "1"
    if request.method == "POST":
        cart = _cart(request, r)
        item_id = request.POST.get("item_id"); action = request.POST.get("action")
        if item_id:
            if action == "add": cart[item_id] = cart.get(item_id, 0) + 1
            elif action == "remove":
                cart[item_id] = cart.get(item_id, 0) - 1
                if cart[item_id] <= 0: cart.pop(item_id, None)
            _save_cart(request, r, cart)
        # Redirect back to the same item (anchor) with the same filters, so
        # the customer sees the stepper change in place instead of a bare
        # reload with no feedback. "added" drives the one-line toast.
        params = []
        if code: params.append(f"table={code}")
        if q: params.append(f"q={q}")
        if veg_only: params.append("veg=1")
        if item_id and action == "add": params.append(f"added={item_id}")
        qs = ("?" + "&".join(params)) if params else ""
        anchor = f"#item-{item_id}" if item_id else ""
        return redirect(f"/r/{slug}/{qs}{anchor}")
    cart_qty, cart_count, cart_total = _cart_totals(request, r)
    categories_data = []
    for c in r.categories.prefetch_related("items").all():
        items = []
        for item in c.items.all():
            if not item.is_available: continue
            if veg_only and not item.is_veg: continue
            if q and q.lower() not in item.name.lower() and q.lower() not in (item.description or "").lower(): continue
            # Attach the session-cart quantity to the item so the template
            # can render Add vs. stepper without a custom template filter.
            item.cart_qty = cart_qty.get(item.id, 0)
            items.append(item)
        if items: categories_data.append((c, items))
    added_name = None
    added_id = request.GET.get("added")
    if added_id:
        added_item = MenuItem.objects.filter(id=added_id, restaurant=r).first()
        if added_item: added_name = added_item.name
    return render(request, "core/public_menu.html", {
        "r": r, "table": table, "categories": categories_data, "cart": _cart(request, r),
        "cart_qty": cart_qty, "cart_count": cart_count, "cart_total": cart_total,
        "q": q, "veg_only": veg_only, "added_name": added_name, "table_code": code,
    })

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
    if request.method == "POST":
        if "remove_item" in request.POST:
            cart.pop(str(request.POST.get("remove_item")), None)
            _save_cart(request, r, cart)
            return redirect(f"/r/{slug}/cart/{'?table=' + code if code else ''}")
        # Stepper on the cart page: same Add/Remove actions as the menu,
        # so quantity is changed where the customer is looking at it.
        if request.POST.get("item_id") and request.POST.get("action") in ("add", "remove"):
            item_id = str(request.POST.get("item_id"))
            if request.POST.get("action") == "add": cart[item_id] = cart.get(item_id, 0) + 1
            else:
                cart[item_id] = cart.get(item_id, 0) - 1
                if cart[item_id] <= 0: cart.pop(item_id, None)
            _save_cart(request, r, cart)
            return redirect(f"/r/{slug}/cart/{'?table=' + code if code else ''}")
        if items:
            order = Order.objects.create(restaurant=r, table=table, note=request.POST.get("note","")[:300])
            for item, qty, _ in items:
                OrderItem.objects.create(order=order, menu_item=item, quantity=qty, unit_price=item.price)
            _save_cart(request, r, {})
            return redirect(f"/r/{slug}/track/{order.id}/")
    gst = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
    return render(request, "core/cart.html", {"r": r, "table": table, "table_code": code, "items": items, "subtotal": subtotal, "gst": gst, "total": subtotal + gst})

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
    cat_form, item_form = CategoryForm(), MenuItemForm(restaurant=r)
    if request.method == "POST":
        # NOTE: do NOT branch on "category" here — MenuItemForm itself has a
        # field named "category", so every item submission contains it and
        # was previously misrouted into the category branch and silently
        # dropped. Branch on the hidden submit markers instead.
        if "add_category" in request.POST:
            cat_form = CategoryForm(request.POST)
            if cat_form.is_valid():
                obj = cat_form.save(commit=False); obj.restaurant = r; obj.save(); return redirect("menu_manage", slug=slug)
            messages.error(request, "Category could not be added. Check the name and sort order.")
        elif "toggle" in request.POST:
            item = get_object_or_404(MenuItem, id=request.POST.get("toggle"), restaurant=r)
            item.is_available = not item.is_available; item.save(); return redirect("menu_manage", slug=slug)
        elif "add_item" in request.POST:
            item_form = MenuItemForm(request.POST, request.FILES, restaurant=r)
            if item_form.is_valid():
                obj = item_form.save(commit=False); obj.restaurant = r; obj.save(); return redirect("menu_manage", slug=slug)
            messages.error(request, "Item could not be added. Check the category, name and price.")
    return render(request, "core/menu_manage.html", {"r": r, "cat_form": cat_form, "item_form": item_form})

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
