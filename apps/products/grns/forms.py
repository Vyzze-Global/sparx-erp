from django import forms
from django.forms import inlineformset_factory
from apps.products.models import GoodsReceiptNote, GoodsReceiptNoteItem, Warehouse, Batch, ProductVariation

class GoodsReceiptNoteForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptNote
        fields = ['purchase_order', 'grn_date', 'reference_number', 'status', 'supplier_reference_number', 'warehouse', 'attachment', 'remarks']
        widgets = {
            'purchase_order': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'status': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'grn_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class GoodsReceiptNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptNote
        fields = ['purchase_order', 'grn_date', 'reference_number', 'status', 'supplier_reference_number', 'warehouse', 'attachment', 'remarks']
        widgets = {
            'purchase_order': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2', 'required': 'required'}),
            'status': forms.Select(attrs={'hidden': 'hidden'}),
            'grn_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class GoodsReceiptNoteItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptNoteItem
        fields = ['grn', 'variation', 'batch', 'po_item', 'quantity_received', 'unit_price', 'is_free_item']
        widgets = {
            'variation': forms.Select(attrs={'class': 'form-select d-none'}),  # Hidden to match PO item
            'batch': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id':'unitprice-input'}),
            'is_free_item': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Inline formset to attach items to a GRN
GoodsReceiptNoteItemFormSet = inlineformset_factory(
    GoodsReceiptNote,
    GoodsReceiptNoteItem,
    form=GoodsReceiptNoteItemForm,
    extra=0,
    can_delete=True
)