from django import forms
from apps.products.models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        exclude = ['variation', 'batch']
        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reserved_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': False}),
        }

class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        exclude = ['variation', 'batch', 'warehouse']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reserved_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }