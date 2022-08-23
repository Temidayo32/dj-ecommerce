# Generated by Django 4.1 on 2022-08-18 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="discount_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
