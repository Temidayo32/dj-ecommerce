from django.contrib import admin

from .models import Product, OrderProduct, Cart, UserProfile, Coupon

# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Coupon)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'original_price', 'discount_price', 'is_bestseller', 'is_featured', 'is_new']
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Product, ProductAdmin)
admin.site.register(OrderProduct)
admin.site.register(Cart)