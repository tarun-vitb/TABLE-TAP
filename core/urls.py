from django.urls import path
from . import views
urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/restaurant/new/", views.restaurant_new, name="restaurant_new"),
    path("dashboard/<slug:slug>/", views.restaurant_dashboard, name="restaurant_dashboard"),
    path("dashboard/<slug:slug>/menu/", views.menu_manage, name="menu_manage"),
    path("dashboard/<slug:slug>/tables/", views.tables_manage, name="tables_manage"),
    path("dashboard/<slug:slug>/tables/<int:table_id>/qr.png", views.table_qr, name="table_qr"),
    path("dashboard/<slug:slug>/kds/", views.kds, name="kds"),
    path("dashboard/<slug:slug>/orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("r/<slug:slug>/", views.public_menu, name="public_menu"),
    path("r/<slug:slug>/cart/", views.cart_view, name="cart_view"),
    path("r/<slug:slug>/track/<int:order_id>/", views.track_order, name="track_order"),
]
