# Generated by Django 4.1 on 2022-08-26 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0003_cart_ordered_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_image",
            field=models.ImageField(
                height_field=10, upload_to="image/", width_field=10
            ),
        ),
    ]