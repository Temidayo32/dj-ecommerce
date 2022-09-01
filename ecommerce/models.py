import email
from operator import truediv
import turtle
import decimal
from django.db import models
from django.conf import settings 
from django.shortcuts import render
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
import sys
from django_countries.fields import CountryField

# Create your models here.


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null= True)
    on_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    title = models.CharField(max_length=100)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2 , blank=True, null=True)
    product_image = models.ImageField(upload_to= "image/")
    slug = models.SlugField(unique=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ecommerce:product-detail", kwargs={"slug": self.slug}
        )
    
    def get_add_to_cart_url(self):
        return reverse("ecommerce:add-to-cart", kwargs={
            'slug': self.slug,
        })
    def get_add_to_cart1_url(self):
        return reverse("ecommerce:add-to-cart-list", kwargs={
            'slug': self.slug,
        })
    def get_remove_from_cart(self):
        return reverse("ecommerce:remove-from-cart", kwargs={
            'slug':self.slug,
        })
    def get_remove1_from_cart(self):
        return reverse("ecommerce:remove-from-cart-list", kwargs={
            'slug':self.slug,
        })
    

    def get_remove_one_item(self):
        return reverse("ecommerce:remove-one-item", kwargs={
            'slug':self.slug,
        })
    def get_remove1_one_item(self):
        return reverse("ecommerce:remove-one-item-list", kwargs={
            'slug':self.slug,
        })

    def save(self, *args, **kwargs):
		#Opening the uploaded image
        img = Image.open(self.product_image)
        output = BytesIO()

		#Resize/modify the image
        img.resize( (100,100) )

		#after modifications, save it to the output
        img.save(output, format='JPEG', quality=100)
        output.seek(0)

		#change the imagefield value to be the newley modifed image value
        self.product_image = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.product_image.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)

        super().save(*args, **kwargs)
 
class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"You've added {self.quantity} item(s) of {self.product.title} "

    def get_total_product_price(self):
        return self.quantity * self.product.original_price
    
    def get_discounted_product_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_discounted_product_price()
    
    def get_final_price(self):
        if self.product.discount_price:
            return self.get_discounted_product_price()
        return self.get_total_product_price()


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    orderproduct = models.ManyToManyField(OrderProduct)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete= models.SET_NULL, blank = True, null= True)
    billing_address = models.ForeignKey('Address', related_name= "billing_address", on_delete = models.SET_NULL, blank=True, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank= True, null = True)
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default= False)


    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.orderproduct.all():
            total += order_item.get_final_price()

        if self.coupon:
            total -= decimal.Decimal(self.coupon.amount)
        return total

class Address(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    country = CountryField(multiple=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Addresses"

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null = True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username





class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()


    def __str__(self):
        return self.code


class Refund(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=True)
    email = models.EmailField()



def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)







