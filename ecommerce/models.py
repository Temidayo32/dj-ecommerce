from django.db import models
from django.conf import settings 
from django.shortcuts import render
from django.urls import reverse

# Create your models here.
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
    def get_remove_from_cart(self):
        return reverse("ecommerce:remove-from-cart", kwargs={
            'slug':self.slug,
        })

    def get_remove_one_item(self):
        return reverse("ecommerce:remove-one_item", kwargs={
            'slug':self.slug,
        })
 
class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"You've added {self.quantity} item(s) of {self.product.title} "



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    orderproduct = models.ManyToManyField(OrderProduct)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.user.username


