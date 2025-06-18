from django import forms
from apps.products.models import Department
from django.utils.text import slugify

class DepartmentForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Department
        fields = ['name', 'description', 'slug', 'ref_1']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'ref_1': forms.TextInput(attrs={'class': 'form-control'}),
        }