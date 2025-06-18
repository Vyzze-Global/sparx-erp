from django import forms
from apps.products.models import Category, Type, Department
from django.utils.text import slugify

class CategoryForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Category
        fields = ['name', 'display_name', 'slug', 'icon', 'image', 'details', 'hide', 'type', 'department', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }