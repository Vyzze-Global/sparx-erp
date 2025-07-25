# Generated by Django 5.0.6 on 2025-06-22 14:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_batch_stock_quantity_inventory_is_primary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodsreceiptnoteitem',
            name='warehouse',
        ),
        migrations.AddField(
            model_name='goodsreceiptnote',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.warehouse'),
        ),
        migrations.AlterField(
            model_name='productvariation',
            name='sku',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
