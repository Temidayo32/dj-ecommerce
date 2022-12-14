# Generated by Django 4.1 on 2022-08-30 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0015_coupon"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="being_delivered",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cart",
            name="coupon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ecommerce.coupon",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="payment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ecommerce.payment",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="received",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cart",
            name="ref_code",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="cart",
            name="refund_granted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cart",
            name="refund_requested",
            field=models.BooleanField(default=False),
        ),
    ]
