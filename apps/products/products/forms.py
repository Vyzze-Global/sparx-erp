from django import forms
from django.forms import inlineformset_factory
from apps.products.models import Product, ProductVariation, Batch

class ProductForm(forms.ModelForm):
    """
    Form for the main Product model.
    """
    # Explicitly define slug to make it not required for form validation
    slug = forms.SlugField(required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'featured_image', 'status', 'is_active',
            'categories', 'brand', 'department', 'supplier', 'tags', 'unit',
            'is_allowed_decimal_quantity', 'non_discount_item'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Select Categories'}),
            'brand': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Select Brand'}),
            'department': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Select Department'}),
            'supplier': forms.SelectMultiple(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Select Supplier'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Select Tags'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'is_allowed_decimal_quantity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'non_discount_item': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductVariationForm(forms.ModelForm):
    """
    Form for an individual ProductVariation.
    """
    sku = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'SKU'})
    )
    cartesian_product_key = forms.CharField(required=False, widget=forms.HiddenInput())


    class Meta:
        model = ProductVariation
        fields = [
            'title', 'cartesian_product_key', 'sku', 'barcode',
            'standard_price', 'standard_sale_price', 'image', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'readonly': 'readonly'}),
            # The 'sku' entry here is no longer needed but leaving it doesn't cause harm.
            'barcode': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Barcode'}),
            'standard_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Std. Price'}),
            'standard_sale_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Std. Sale Price'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input form-check-sm'}),
        }

# Formset for managing multiple variations tied to a single product.
VariationFormSet = inlineformset_factory(
    Product,
    ProductVariation,
    form=ProductVariationForm,
    extra=0,
    can_delete=True,
    fk_name='product'
)