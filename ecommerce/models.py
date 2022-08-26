from django.db import models
from django.conf import settings 
from django.shortcuts import render
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

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


    def __str__(self):
        return self.user.username


