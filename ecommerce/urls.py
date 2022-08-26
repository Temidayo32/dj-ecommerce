from django.urls import path

from .views import (
    ProductListView,
    ProductDetailView,
    OrderSummaryView,
    add_to_cart,
    add_to_cart_summary,
    remove_from_cart,
    remove_from_cart_summary,
    remove_one_item,
    add_to_cart_list,
    remove_from_cart_list,
    remove_one_item_list,
    add_to_cart_summary,
    remove_one_item_summary,
    remove_from_cart_summary,
    
)


app_name= "ecommerce"

urlpatterns = [
    path('', ProductListView.as_view(), name= "product-list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name= "product-detail"),
    
    path("add-to-cart/<slug:slug>/", add_to_cart, name = "add-to-cart"),
    path("remove-from-cart/<slug:slug>/",remove_from_cart, name= "remove-from-cart"),
    path("add-to-cart-list/<slug:slug>/", add_to_cart_list, name = "add-to-cart-list"),
    path("add-to-cart-summary/<slug:slug>/", add_to_cart_summary, name = "add-to-cart-summary"),

    path("remove-from-cart-list/<slug:slug>/",remove_from_cart_list, name= "remove-from-cart-list"),
    path("remove-from-cart-summary/<slug:slug>/",remove_from_cart_summary, name= "remove-from-cart-summary"),

    path("add-to-cart-list/<slug:slug>/", add_to_cart_list, name = "add-to-cart-list"),
    path("remove_one_item/<slug:slug>/", remove_one_item, name= "remove-one-item"),
    path("remove_one_item_summary/<slug:slug>/", remove_one_item_summary, name= "remove-one-item-summary"),

    
    path("remove_one_item_list/<slug:slug>/", remove_one_item_list, name= "remove-one-item-list"),
    path("order-summary", OrderSummaryView.as_view(), name = "order-summary")

]