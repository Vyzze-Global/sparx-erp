# Generated by Django 5.0.6 on 2025-06-18 03:35

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, null=True, unique=True)),
                ('logo', models.ImageField(blank=True, help_text='Brand Logo', null=True, upload_to='brands/')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, null=True, unique=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('ref_1', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('bank_details', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('image', models.JSONField(blank=True, default=dict, null=True)),
                ('icon', models.JSONField(blank=True, default=dict, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('image', models.ImageField(help_text='Type Image', null=True, upload_to='types/')),
                ('banners', models.JSONField(blank=True, default=list, null=True)),
                ('promotional_sliders', models.JSONField(blank=True, default=list, null=True)),
                ('settings', models.JSONField(blank=True, default=dict, null=True)),
                ('icon', models.CharField(blank=True, default='default_icon', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
                ('is_primary', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='products.attribute')),
            ],
            options={
                'unique_together': {('attribute', 'value')},
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, null=True, unique=True)),
                ('display_name', models.CharField(max_length=255, null=True, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, help_text='Category Image', null=True, upload_to='categories/')),
                ('details', models.TextField(blank=True, null=True)),
                ('hide', models.BooleanField(blank=True, default=False, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.category')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.department')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.type')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('featured_image', models.ImageField(blank=True, help_text='Featured Image', null=True, upload_to='products/')),
                ('in_stock', models.BooleanField(default=True)),
                ('unit', models.CharField(blank=True, default='1 Stk', max_length=50, null=True)),
                ('ratings', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('total_reviews', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('publish', 'Publish'), ('draft', 'Draft')], max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_allowed_decimal_quantity', models.BooleanField(default=False)),
                ('non_discount_item', models.BooleanField(default=False)),
                ('brand', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.brand')),
                ('categories', models.ManyToManyField(blank=True, to='products.category')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.department')),
                ('supplier', models.ManyToManyField(blank=True, to='products.supplier')),
                ('tags', models.ManyToManyField(blank=True, to='products.tag')),
                ('type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.type')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('image', models.ImageField(help_text='Product gallery image', upload_to='product_images/')),
                ('alt_text', models.CharField(blank=True, help_text='Alternative text for accessibility', max_length=255, null=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of display in gallery')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, help_text='Variation Title', max_length=255, null=True)),
                ('cartesian_product_key', models.CharField(db_index=True, max_length=255, null=True)),
                ('sku', models.CharField(blank=True, max_length=100, null=True)),
                ('barcode', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('standard_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('standard_sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('image', models.ImageField(blank=True, help_text='Variation Image', null=True, upload_to='products/')),
                ('stock_quantity', models.IntegerField(blank=True, null=True)),
                ('stock_threshold', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variations', to='products.product')),
            ],
            options={
                'unique_together': {('product', 'cartesian_product_key')},
            },
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('batch_number', models.CharField(max_length=100)),
                ('stock_quantity', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('manufactured_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('wholesale_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('variation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='products.productvariation')),
            ],
            options={
                'unique_together': {('variation', 'batch_number')},
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('po_number', models.IntegerField(null=True, unique=True)),
                ('order_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('partially_received', 'Partially Received'), ('fully_received', 'Fully Received'), ('cancelled', 'Cancelled')], default='draft', max_length=20)),
                ('expected_delivery_date', models.DateField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='po_approved_by', to='accounts.employeeprofile')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.supplier')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='GoodsReceiptNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('grn_number', models.IntegerField(unique=True)),
                ('grn_date', models.DateField(blank=True, null=True)),
                ('reference_number', models.CharField(blank=True, max_length=100, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('received_date', models.DateTimeField(blank=True, null=True)),
                ('supplier_reference_number', models.CharField(blank=True, max_length=50, null=True)),
                ('attachment', models.ImageField(blank=True, null=True, upload_to='grns/')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('received', 'Received'), ('inspected', 'Inspected'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft', max_length=20)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('checked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grn_checked_by', to='accounts.employeeprofile')),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.employeeprofile')),
                ('purchase_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('expected_delivery_date', models.DateField(blank=True, null=True)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='products.purchaseorder')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productvariation')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseReturn',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('return_number', models.IntegerField(unique=True)),
                ('attachment', models.ImageField(blank=True, null=True, upload_to='purchase-returns/')),
                ('return_date', models.DateField(auto_now_add=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('reason', models.TextField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('approved', 'Approved'), ('partially_received', 'Partially Received'), ('fully_received', 'Fully Received'), ('cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_return_approved_by', to='accounts.employeeprofile')),
                ('grn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.goodsreceiptnote')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.supplier')),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.type'),
        ),
        migrations.CreateModel(
            name='PurchaseReturnItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.FloatField(blank=True, default=0.0, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.batch')),
                ('return_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='products.purchasereturn')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productvariation')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='GoodsReceiptNoteItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity_received', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('free_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_free_item', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.batch')),
                ('grn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='products.goodsreceiptnote')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productvariation')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariationOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.attribute')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.attributevalue')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='products.productvariation')),
            ],
            options={
                'unique_together': {('variation', 'attribute')},
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('reserved_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.batch')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productvariation')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.warehouse')),
            ],
            options={
                'unique_together': {('warehouse', 'variation', 'batch')},
            },
        ),
    ]
