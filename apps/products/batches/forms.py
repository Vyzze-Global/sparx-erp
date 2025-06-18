from django import forms
from apps.products.models import Batch

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            'batch_number', 'cost_price', 'price', 'sale_price',
            'stock_quantity', 'manufactured_date', 'expiry_date', 'is_active'
        ]
        widgets = {
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'manufactured_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }