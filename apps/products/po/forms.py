from django import forms
from django.forms import inlineformset_factory
from apps.products.models import PurchaseOrder, PurchaseOrderItem, ProductVariation, Supplier, Warehouse

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'warehouse', 'order_date', 'status',
            'expected_delivery_date', 'notes'
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'warehouse': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'hidden': 'hidden'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'variation', 'unit_price', 'quantity', 'expected_delivery_date'
        ]
        widgets = {
            'variation': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2', 'hidden': 'hidden'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# Inline formset to attach multiple items to a single PurchaseOrder
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=0,
    can_delete=True
)