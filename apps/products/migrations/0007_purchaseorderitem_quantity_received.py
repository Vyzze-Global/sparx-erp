# Generated by Django 5.0.6 on 2025-06-26 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_goodsreceiptnoteitem_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='quantity_received',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10),
        ),
    ]
