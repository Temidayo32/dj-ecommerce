from time import timezone
from webbrowser import get
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
# Create your views here.
from .models import OrderProduct, Product, Cart
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 

class ProductListView(ListView):
    template_name= "product-list.html"
    model = Product

    
    
    def get_queryset(self):
        queryset = Product.objects.all()
        query_search = self.request.GET.get('search')

        if query_search:
            queryset = Product.objects.filter(Q(title__icontains=query_search)| Q(description__icontains=query_search)).distinct()

        return queryset

        

class ProductDetailView(DetailView):
    model = Product
    template_name = "product-detail.html"

@login_required
def add_to_cart(request, slug):
        order = get_object_or_404(Product, slug=slug)
        ordering, created = OrderProduct.objects.get_or_create(
            product=order,
            user = request.user,
            ordered = False,
        )
        cart_qs = Cart.objects.filter(user =request.user, ordered= False)

        if cart_qs.exists():
            new_cart = cart_qs[0]
            if new_cart.orderproduct.filter(product__slug=order.slug).exists():
                ordering.quantity += 1
                ordering.save()
                messages.info(request, "This item was successfully added to your cart" )
                return redirect(reverse("ecommerce:product-list"))  #, kwargs={'slug':slug,}
                

            else:
                new_cart.orderproduct.add(ordering)
                messages.info(request, "This item was successfully added to your cart")
                ordering.save()
                return redirect(reverse("ecommerce:product-list")) #, kwargs={'slug':slug,}
        
        else:
            ordered = timezone.now()
            new_cart = Cart.objects.create(
                user = request.user,
                ordered_date = ordered,
            )
            new_cart.orderproduct.add(ordering)
            ordering.save()
            messages.info(request, "This item was successfully added to your cart")
            return redirect(reverse("ecommerce:product-detail"))   #, kwargs={'slug':slug,}


@login_required
def remove_from_cart(request, slug):
    order = get_object_or_404(Product, slug=slug)

    cart_qs =Cart.objects.filter(user=request.user, ordered=False)
    

    if cart_qs.exists():
        new_cart = cart_qs[0]
        if new_cart.orderproduct.filter(product__slug=order.slug).exists():
            ordering = OrderProduct.objects.filter(product=order, user = request.user, ordered = False)[0]
            new_cart.orderproduct.remove(ordering)
            ordering.delete()
            messages.info(request, "This item was successfully removed from your cart")
            return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))

        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))

@login_required
def remove_one_item(request, slug):
    order = get_object_or_404(Product, slug=slug)

    cart_qs =Cart.objects.filter(user=request.user, ordered=False)
    

    if cart_qs.exists():
        new_cart = cart_qs[0]
        if new_cart.orderproduct.filter(product__slug=order.slug).exists():
            ordering = OrderProduct.objects.filter(product=order, user = request.user, ordered = False)[0]
            if ordering.quantity > 1:
                ordering.quantity -= 1
                ordering.save()
            else:
                new_cart.orderproduct.remove(ordering)
                ordering.delete()
            messages.info(request, "This item was successfully updated")
            return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))


        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))








 