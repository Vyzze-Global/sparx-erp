import uuid

from django.db import models, transaction
from django.db.models import F, Sum
from auth.models import EmployeeProfile
from django.utils.text import slugify
from django.core.exceptions import ValidationError

def get_unique_slug(model, base_slug, max_length):
    """Generate a unique slug by appending -number if needed."""
    slug = base_slug[:max_length]
    counter = 1
    original_slug = slug
    while model.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{original_slug[:max_length - len(str(counter)) - 1]}-{counter}"
    return slug

class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Type(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=20, blank=True, unique=True, null=True)
    image = models.ImageField(upload_to="types/", null=True, help_text="Type Image")
    banners = models.JSONField(default=list, blank=True, null=True)
    promotional_sliders = models.JSONField(default=list, blank=True, null=True)
    settings = models.JSONField(default=dict, blank=True, null=True)
    icon = models.CharField(max_length=20, default='default_icon', blank=True, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    ref_1 = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            self.slug = get_unique_slug(Department, base_slug, 255)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, null=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True, help_text="Brand Logo")
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Supplier"


class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True, null=True)
    display_name = models.CharField(max_length=255, unique=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True, help_text="Category Image")
    details = models.TextField(null=True, blank=True)
    hide = models.BooleanField(default=False, blank=True, null=True)

    type = models.ForeignKey(Type, on_delete=models.SET_NULL, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            self.slug = get_unique_slug(Category, base_slug, 255)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    icon = models.JSONField(default=dict, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            self.slug = get_unique_slug(Attribute, base_slug, 255)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"


class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)

    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(upload_to="products/", blank=True, null=True, help_text="Featured Image")
    in_stock = models.BooleanField(default=True)
    unit = models.CharField(max_length=50, default='1 Stk', blank=True, null=True)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, choices=[('publish', 'Publish'), ('draft', 'Draft')])
    is_active = models.BooleanField(default=True)
    is_allowed_decimal_quantity = models.BooleanField(default=False)
    non_discount_item = models.BooleanField(default=False)

    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL, default=None)
    categories = models.ManyToManyField(Category, blank=True)
    brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.SET_NULL, default=None)
    department = models.ForeignKey(Department, blank=True, null=True, on_delete=models.SET_NULL)
    supplier = models.ManyToManyField(Supplier, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            self.slug = get_unique_slug(Product, base_slug, 255)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/", help_text="Product gallery image")
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Alternative text for accessibility")
    order = models.PositiveIntegerField(default=0, help_text="Order of display in gallery")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name} (Order: {self.order})"


class ProductVariation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Variation Title")
    cartesian_product_key = models.CharField(max_length=255, db_index=True, null=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)

    standard_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    standard_sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    image = models.ImageField(upload_to="products/", blank=True, null=True, help_text="Variation Image")
    stock_quantity = models.IntegerField(blank=True, null=True)
    stock_threshold = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # This is the crucial database constraint!
        unique_together = ('product', 'cartesian_product_key')

    def _generate_title(self):
        """Generate title based on variation options."""
        options = self.options.all().select_related('attribute', 'value')
        return " / ".join(option.value.value for option in options) if options else "Default"

    def _generate_cartesian_product_key(self):
        """Generate cartesian product key based on variation options."""
        options = self.options.all().select_related('attribute', 'value')
        return "/".join(option.value.value for option in options) if options else "default"

    def save(self, *args, **kwargs):
        """Update title and cartesian_product_key before saving."""
        if not self.title:
            self.title= self._generate_title()
        if not self.cartesian_product_key:
            self.cartesian_product_key= self._generate_cartesian_product_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.title}"
    
class ProductVariationOption(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    variation = models.ForeignKey(ProductVariation, related_name='options', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variation', 'attribute')  # Enforce uniqueness

    def __str__(self):
        return f"{self.variation.product.name} - {self.attribute.name}: {self.value.value}"


class Batch(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    batch_number = models.CharField(max_length=100)
    manufactured_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)  # For perishable goods
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    is_active = models.BooleanField(default=True)

    variation = models.ForeignKey(ProductVariation, related_name='batches', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variation', 'batch_number')

    def __str__(self):
        return f"Batch {self.batch_number} - {self.variation.product.name}"

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserved_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('warehouse', 'variation', 'batch')

class PurchaseOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    po_number = models.IntegerField(null=True, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('partially_received', 'Partially Received'),
        ('fully_received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ], default='draft')
    expected_delivery_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            # get the highest existing GoodsReceiptNote instance and increment it
            po = PurchaseOrder.objects.order_by('-po_number').first()
            if po is None:
                # if there are no existing Order instances, start from 1
                self.po_number = 1
            else:
                self.po_number = po.po_number + 1

        super().save(*args, **kwargs)

    def update_total(self):
        """
        Update the total of this PurchaseOrder by summing the totals of all related items.
        """
        total = self.items.aggregate(models.Sum('total'))['total__sum'] or 0
        self.total = total
        self.save()

    def __str__(self):
        return f"PO-{self.po_number}"
    
class PurchaseOrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    expected_delivery_date = models.DateField(null=True, blank=True)

    @property
    def quantity_to_receive(self):
        return max(self.quantity - self.quantity_received, 0)
    
    @property
    def entered_quantity_to_receive(self):
        # Sum the quantity_received from GoodsReceiptNoteItems where the GRN status is not 'received' or 'rejected'
        entered_quantity = self.grn_items.filter(
            grn__status__in=['draft', 'inspected', 'approved']
        ).aggregate(total=Sum('quantity_received'))['total'] or 0
        return entered_quantity

    def save(self, *args, **kwargs):
        # Calculate the total for this item
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update the parent PurchaseOrder's total
        self.purchase_order.update_total()

    def delete(self, *args, **kwargs):
        # Store the purchase order reference before deletion
        purchase_order = self.purchase_order
        super().delete(*args, **kwargs)
        # Update the parent PurchaseOrder's total after deletion
        purchase_order.update_total()

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.variation.product.name}"

class GoodsReceiptNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grn_number = models.IntegerField(unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    grn_date = models.DateField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    received_date = models.DateTimeField(null=True, blank=True)
    supplier_reference_number = models.CharField(max_length=50, null=True, blank=True)
    attachment = models.ImageField(upload_to='grns/', blank=True, null=True)
    received_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True)
    checked_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='grn_checked_by')
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('inspected', 'Inspected'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.grn_number:
            # get the highest existing GoodsReceiptNote instance and increment it
            grn = GoodsReceiptNote.objects.order_by('-grn_number').first()
            if grn is None:
                # if there are no existing Order instances, start from 1
                self.grn_number = 1
            else:
                self.grn_number = grn.grn_number + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"GRN-{self.grn_number}"
    
class GoodsReceiptNoteItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='grn_items')
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    is_free_item = models.BooleanField(default=False)

    def clean(self):
        # Validate quantity for non-free items against PO
        if self.po_item and not self.is_free_item:
            total_received = (
                GoodsReceiptNoteItem.objects
                .filter(po_item=self.po_item, is_free_item=False)
                .exclude(id=self.id)
                .aggregate(Sum('quantity_received'))['quantity_received__sum'] or 0
            )
            total_received += self.quantity_received or 0

            if total_received > self.po_item.quantity:
                raise ValidationError({
                    'quantity_received': (
                        f"Exceeds ordered quantity ({self.po_item.quantity}) for non-free items."
                    )
                })

        # Check for duplicate batches based on free/non-free status
        if self.batch:
            # If this is a free item, ensure no other free item with the same batch exists in the GRN
            if self.is_free_item:
                duplicate_free = (
                    GoodsReceiptNoteItem.objects
                    .filter(
                        grn=self.grn,
                        batch=self.batch,
                        is_free_item=True
                    )
                    .exclude(id=self.id)
                    .exists()
                )
                if duplicate_free:
                    raise ValidationError({
                        'batch': (
                            f"Batch {self.batch} is already used for a free item in this GRN."
                        )
                    })
            # If this is a non-free item, ensure no other non-free item with the same batch exists in the GRN
            else:
                duplicate_non_free = (
                    GoodsReceiptNoteItem.objects
                    .filter(
                        grn=self.grn,
                        batch=self.batch,
                        is_free_item=False
                    )
                    .exclude(id=self.id)
                    .exists()
                )
                if duplicate_non_free:
                    raise ValidationError({
                        'batch': (
                            f"Batch {self.batch} is already used for a non-free item in this GRN."
                        )
                    })

    def save(self, *args, **kwargs):
        quantity = max(self.quantity_received, 0) if self.quantity_received else 0
        # Set total to 0 for free items, otherwise calculate normally
        self.total = 0 if self.is_free_item else quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update the GRN total by summing the totals of all non-free items
        grn_total = (
            GoodsReceiptNoteItem.objects
            .filter(grn=self.grn, is_free_item=False)
            .aggregate(Sum('total'))['total__sum'] or 0
        )
        self.grn.total = grn_total
        self.grn.save()

    def delete(self, *args, **kwargs):
        quantity = max(self.quantity_received, 0) if self.quantity_received else 0
        # Set total to 0 for free items, otherwise calculate normally
        self.total = 0 if self.is_free_item else quantity * self.unit_price
        super().delete(*args, **kwargs)

        # Update the GRN total by summing the totals of all non-free items
        grn_total = (
            GoodsReceiptNoteItem.objects
            .filter(grn=self.grn, is_free_item=False)
            .aggregate(Sum('total'))['total__sum'] or 0
        )
        self.grn.total = grn_total
        self.grn.save()

    def __str__(self):
        return f"{self.grn.grn_number} - {self.variation.product.name}"

class PurchaseReturn(models.Model):
    STATUS = [
        ('Pending', 'Pending'),
        ('approved', 'Approved'),
        ('partially_received', 'Partially Received'),
        ('fully_received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_number = models.IntegerField(unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.SET_NULL, null=True, blank=True)
    attachment = models.ImageField(upload_to='purchase-returns/', blank=True, null=True)
    return_date = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_return_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.return_number:
            # get the highest existing GoodsReceiptNote instance and increment it
            return_number = PurchaseReturn.objects.order_by('-return_number').first()
            if return_number is None:
                # if there are no existing Order instances, start from 1
                self.return_number = 1
            else:
                self.return_number = return_number.return_number + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return Order-{self.return_number}"

class PurchaseReturnItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_order = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name="items")
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.FloatField(null=True, blank=True, default=0.00)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.return_order.return_number} - {self.variation.product.name}"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('sales_return', 'Sales Return'),
        ('purchase', 'Purchase'),
        ('purchase_return', 'Purchase Return'),
        ('expiry', 'Expiry'),
        ('damage', 'Damage'),
        ('other', 'Other'),
    ]

    ADJUSTMENT_TYPES = [('in', 'In'), ('out', 'Out')]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.SET_NULL)
    warehouse = models.ForeignKey(Warehouse, null=True, blank=True, on_delete=models.SET_NULL)

    # Optional relations for traceability
    purchase_order = models.ForeignKey(PurchaseOrder, null=True, blank=True, on_delete=models.SET_NULL)
    grn = models.ForeignKey(GoodsReceiptNote, null=True, blank=True, on_delete=models.SET_NULL)
    purchase_return = models.ForeignKey(PurchaseReturn, null=True, blank=True, on_delete=models.SET_NULL)
    order_return = models.ForeignKey('orders.orderreturn', null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey('orders.order', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.variation.product.name} - {self.quantity} ({self.adjustment_type})"