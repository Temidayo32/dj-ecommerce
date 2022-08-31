from multiprocessing import AuthenticationError
from time import timezone
from webbrowser import get
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from .models import OrderProduct, Product, Cart, Address, UserProfile, Coupon, Payment
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import random
import string

from .forms import CheckoutForm, StripePaymentForm, CouponForm

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

def ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Cart.objects.get(user=self.request.user, ordered = False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True
            }

            ship_address = Address.objects.filter(user = self.request.user, address_type = 'S', default= True)
            if ship_address.exists():
                context.update({"default_shipping_address": ship_address[0]})

            bill_address = Address.objects.filter(user = self.request.user, address_type = 'B', default = True)
            
            if bill_address.exists():
                context.update({'default_billing_address': bill_address[0]})
            return render( self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("ecommerce:checkout")


    # def post(self, *args, **kwargs):
    #     form = CheckoutForm(self.request.POST or None)
    #     print(self.request.POST)
    #     if form.is_valid():
    #         print(form.cleaned_data)
    #         print("This form is valid")
    #         messages.info(self.request, "Checkout successful!")
    #         return redirect("ecommerce:checkout")
    #     messages.info(self.request, "Failed Checkout")
    #     return redirect("ecommerce:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try: 
            order = Cart.objects.get(user=self.request.user,ordered = False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(user=self.request.user, address_type="S", default=True)
                    
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect("core:checkout")
                else:
                    print("User in entering a new shipping address")
                    shipping_address = form.cleaned_data.get("shipping_address")
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip =form.cleaned_data.get('shipping_zip')
                    
                    if is_valid_form([shipping_address, shipping_country, shipping_zip]):
                        shipping_address= Address(
                            user=self.request.user,street_address = shipping_address, apartment_address= shipping_address2, country = shipping_country, zip= shipping_zip, address_type = 'S'
                        ) 
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping= form.cleaned_data.get('set_default_shipping')

                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required address fields")
                
                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()


                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(user= self.request.user, address_type ='B', default= True)

                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('ecommerce:checkout')
                
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get("billing_address2")
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user = self.request.user, street_address = billing_address1, apartment_address = billing_address2, country = billing_country, zip= billing_zip, address_type = 'B')
                        
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')

                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    

                    else:
                        messages.info(self.request, "Please fil in the required billing address fields")
                  
            payment_option = form.cleaned_data.get('payment_option')

            if payment_option == "S":
                return redirect("ecommerce:payment", payment_option = 'stripe')
            elif payment_option =='P':
                return redirect("ecommerce:payment", paymente_option= 'paypal')
            else:
                messages.warning(self.request, "Invalid payment option selected")
            return redirect("ecommerce:checkout")
        
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("ecommerce:order-summary")




class PaymentView(View):
    def get(self, *args, **kwargs):
        cart  = Cart.objects.get(user = self.request.user, ordered = False)

        if cart.billing_address:
            
            context = {
                'order': cart,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY,
                'DISPLAY_COUPON_FORM': False
            }
        userprofile = self.request.user.userprofile

        if userprofile.on_click_purchasing:
            cards = stripe.Customer.list_sources(userprofile.stripe_customer_id, limit=3, object='card'
            )
            card_list = cards['data']
            if len(card_list) > 0:
                context.update({
                    'card': card_list[0]
                })
        return render(self.request, "payment.html", context)
    
    def post(self, *args, **kwargs):
        cart = Cart.objects.get(user = self.request.user, ordered = False)
        
        form = StripePaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user= self.request.user)
        
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id  != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(userprofile.stripe_customer_id)

                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create( email = self.request.user.email,)

                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.on_click_purchasing = True
                    userprofile.save()

            amount = int(cart.get_total() * 100)

            try:
                if use_default or save:
                    charge = stripe.Charge.create(amount=amount, currency="usd", customer=userprofile.stripe_customer_id)

                else:
                    charge = stripe.Charge.create(amount=amount, currency= 'usd', source=token)

                payment = Payment()
                payment.stripe_charge_id= charge['id']
                payment.user = self.request.user
                payment.amount = cart.get_total()
                payment.save()


                order_items = cart.orderproduct.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                cart.ordered = True
                cart.payment = payment
                cart.ref_code = ref_code()
                cart.save()

                messages.success(self.request, "Your order was successful")
                return redirect('/ecommerce')

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')} ")
                return redirect('/ecommerce')

            except stripe.error.RateLimitError as e:
                messages.warning(self.request, "Rate Limit Error"
                )
                return redirect("/ecommerce")

            except stripe.error.InvalidRequestError as e:
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/ecommerce")

            except stripe.error.AuthenticationError as e:
                messages.warning(self.request, "Not authenticated")
                return redirect("/ecommerce")

            except stripe.error.APIConnectionError as e:
                messages.warning(self.request, "Network error")
                return redirect("/ecommerce")

            except stripe.error.StripeError as e:
                messages.warning(self.request, "Something went wrong. You were not charged. Please try again")

                return redirect("/ecommerce")

            except Exception as e:
                messages.warning(self.request, "A serious error occurred. We have been notified")
                return redirect("/ecommerce")
        
        
        messages.warning(self.request, "Invalid data received")
        return redirect('/payment/stripe')
            
        








class ProductListView(ListView):
    template_name= "product-list.html"
    model = Product  
    
    def get_queryset(self):
        queryset = Product.objects.all()
        query_search = self.request.GET.get('search')

        if query_search:
            queryset = Product.objects.filter(Q(title__icontains=query_search)| Q(description__icontains=query_search)).distinct()

        return queryset
    
    # def get_context_data(self,**kwargs):
    #     context =  super().get_context_data(**kwargs)
    #     query = Product.objects.all()
    #     query_search = self.request.GET.get('search')

    #     if query_search:
    #         query = Product.objects.filter(Q(title__icontains=query_search)| Q(description__icontains=query_search)).distinct()
    #     order = Cart.objects.get(user = self.request.user, ordered = False)
    #     cart = order.orderproduct.all()
        
    #     context['order_item'] = query
    #     context['cart'] = cart
    #     return context  

        

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
                return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}
                ))  #, kwargs={'slug':slug,}
                

            else:
                new_cart.orderproduct.add(ordering)
                messages.info(request, "This item was successfully added to your cart")
                ordering.save()
                return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}
                )) #, kwargs={'slug':slug,}
        
        else:
            ordered = timezone.now()
            new_cart = Cart.objects.create(
                user = request.user,
                ordered_date = ordered,
            )
            new_cart.orderproduct.add(ordering)
            ordering.save()
            messages.info(request, "This item was successfully added to your cart")
            return redirect(reverse("ecommerce:product-detail", kwargs={'slug':slug,}))   #, kwargs={'slug':slug,}


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


def add_to_cart_list(request, slug):
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
            return redirect(reverse("ecommerce:product-list"))   


@login_required
def remove_from_cart_list(request, slug):
    order = get_object_or_404(Product, slug=slug)

    cart_qs =Cart.objects.filter(user=request.user, ordered=False)
    

    if cart_qs.exists():
        new_cart = cart_qs[0]
        if new_cart.orderproduct.filter(product__slug=order.slug).exists():
            ordering = OrderProduct.objects.filter(product=order, user = request.user, ordered = False)[0]
            new_cart.orderproduct.remove(ordering)
            ordering.delete()
            messages.info(request, "This item was successfully removed from your cart")
            return redirect(reverse("ecommerce:product-list"))

        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:product-list"))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:product-list"))

@login_required
def remove_one_item_list(request, slug):
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
            return redirect(reverse("ecommerce:product-list"))


        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:product-list"))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:product-list"))

@login_required
def add_to_cart_summary(request, slug):
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
                return redirect(reverse("ecommerce:order-summary"))  #, kwargs={'slug':slug,}
                

            else:
                new_cart.orderproduct.add(ordering)
                messages.info(request, "This item was successfully added to your cart")
                ordering.save()
                return redirect(reverse("ecommerce:order-summary")) #, kwargs={'slug':slug,}
        
        else:
            ordered = timezone.now()
            new_cart = Cart.objects.create(
                user = request.user,
                ordered_date = ordered,
            )
            new_cart.orderproduct.add(ordering)
            ordering.save()
            messages.info(request, "This item was successfully added to your cart")
            return redirect(reverse("ecommerce:order-summary"))   

@login_required
def remove_one_item_summary(request, slug):
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
            return redirect(reverse("ecommerce:order-summary"))


        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:order-summary"))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:order-summary"))

@login_required
def remove_from_cart_summary(request, slug):
    order = get_object_or_404(Product, slug=slug)

    cart_qs =Cart.objects.filter(user=request.user, ordered=False)
    

    if cart_qs.exists():
        new_cart = cart_qs[0]
        if new_cart.orderproduct.filter(product__slug=order.slug).exists():
            ordering = OrderProduct.objects.filter(product=order, user = request.user, ordered = False)[0]
            new_cart.orderproduct.remove(ordering)
            ordering.delete()
            messages.info(request, "This item was successfully removed from your cart")
            return redirect(reverse("ecommerce:order-summary"))

        else:
            messages.info(request, "This item is not in your cart")
            return redirect(reverse("ecommerce:order-summary"))
    
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect(reverse("ecommerce:order-summary"))



class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            cart = Cart.objects.get(user = self.request.user, ordered = False)
            order_item  = cart.orderproduct.all()
            context = {
                "order_item" : order_item
            }
            return render(self.request, "order-summary.html", context)
            
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect('ecommerce:checkout')

class CouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        print(self.request.POST)
        
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Cart.objects.get(user=self.request.user, ordered = False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added Coupon")
                return redirect("ecommerce:checkout")
            
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("ecommerce:checkout")
            




 