# Generated by Django 5.0.6 on 2025-06-24 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_goodsreceiptnoteitem_po_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodsreceiptnoteitem',
            name='free_quantity',
        ),
    ]
