from django.urls import path

from .views import (
    ProductListView,
    ProductDetailView,
    add_to_cart,
    remove_from_cart,
    remove_one_item,
)


app_name= "ecommerce"

urlpatterns = [
    path('', ProductListView.as_view(), name= "product-list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name= "product-detail"),
    
    path("add-to-cart/<slug:slug>/", add_to_cart, name = "add-to-cart"),
    path("remove-from-cart/<slug:slug>/",remove_from_cart, name= "remove-from-cart"),
    path("remove_one_item/<slug:slug>/", remove_one_item, name= "remove-one-item")
]