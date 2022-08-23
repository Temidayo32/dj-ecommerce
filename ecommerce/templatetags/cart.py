from django import template
from django.shortcuts import get_object_or_404

from ..models import Cart, OrderProduct, Product

register =template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        product_qs =Cart.objects.filter(user=user,ordered=False)
        if product_qs.exists():
            return product_qs[0].orderproduct.count()
    return 0

@register.inclusion_tag("cart.html")
def get_quantity(*args, **kwargs):
    
    id = kwargs['id']
    user = kwargs['user']
    slug = kwargs['slug']
    # order = get_object_or_404(Product, slug=slug)
    cart_qs = Cart.objects.filter(user =user, ordered= False)

    if cart_qs.exists():
         new_cart = cart_qs[0]
         if new_cart.orderproduct.filter(product__slug=slug).exists():
            quantity = get_object_or_404(OrderProduct, product_id=id, user=user, ordered = False)
            num = quantity.quantity
            
            return {
                'num':num
            }
    