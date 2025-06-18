from django.contrib import admin
from .models import (
    Warehouse, Type, Department, Brand, Supplier, Category, Tag,
    Attribute, AttributeValue, Product, ProductImage, ProductVariation,
    ProductVariationOption, Batch, Inventory, PurchaseOrder,
    PurchaseOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem,
    PurchaseReturn, PurchaseReturnItem
)

### Inlines & Utilities

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariationOptionInline(admin.TabularInline):
    model = ProductVariationOption
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    show_change_link = True

class BatchInline(admin.TabularInline):
    model = Batch
    extra = 1

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

class GoodsReceiptNoteItemInline(admin.TabularInline):
    model = GoodsReceiptNoteItem
    extra = 1

class PurchaseReturnItemInline(admin.TabularInline):
    model = PurchaseReturnItem
    extra = 1

### ModelAdmins

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'contact_number', 'is_primary')
    search_fields = ('name', 'code', 'contact_number')
    list_filter = ('is_primary',)
    ordering = ('name',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email')
    search_fields = ('name', 'contact_person', 'email')
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'department', 'type', 'hide')
    search_fields = ('name', 'display_name')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('department', 'type', 'hide')
    raw_id_fields = ('parent',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'type')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('type',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('attribute__name', 'value')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'unit', 'is_active', 'status')
    search_fields = ('name', 'slug', 'description')
    list_filter = ('in_stock', 'is_active', 'status', 'type', 'brand', 'department')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariationInline]

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'title', 'sku', 'barcode', 'standard_price', 'stock_quantity', 'is_active')
    search_fields = ('product__name', 'title', 'sku', 'barcode')
    list_filter = ('is_active',)
    inlines = [ProductVariationOptionInline, BatchInline]

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'variation', 'stock_quantity', 'expiry_date', 'is_active')
    search_fields = ('batch_number', 'variation__product__name')
    list_filter = ('is_active', 'expiry_date')
    raw_id_fields = ('variation',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'variation', 'batch', 'quantity', 'reserved_quantity')
    list_filter = ('warehouse',)
    raw_id_fields = ('variation', 'batch', 'warehouse')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'warehouse', 'status', 'order_date', 'expected_delivery_date', 'total')
    search_fields = ('po_number', 'supplier__name')
    list_filter = ('status', 'order_date', 'expected_delivery_date', 'warehouse')
    inlines = [PurchaseOrderItemInline]
    raw_id_fields = ('supplier', 'warehouse', 'approved_by')

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ('grn_number', 'purchase_order', 'grn_date', 'received_date', 'status')
    search_fields = ('grn_number', 'purchase_order__po_number')
    list_filter = ('status', 'grn_date')
    inlines = [GoodsReceiptNoteItemInline]
    raw_id_fields = ('purchase_order', 'received_by', 'checked_by')

@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ('return_number', 'supplier', 'grn', 'return_date', 'status', 'total')
    search_fields = ('return_number', 'supplier__name')
    list_filter = ('status', 'return_date')
    inlines = [PurchaseReturnItemInline]
    raw_id_fields = ('supplier', 'grn', 'approved_by')

### Optional: registering stand-alone models without inlines

admin.site.register(ProductImage)
admin.site.register(ProductVariationOption)
admin.site.register(PurchaseOrderItem)
admin.site.register(GoodsReceiptNoteItem)
admin.site.register(PurchaseReturnItem)