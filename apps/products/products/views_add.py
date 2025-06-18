from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.transactions.models import Transaction
from apps.transactions.forms import TransactionForm
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin
from apps.products.products.forms import ProductForm, VariationFormSet
from apps.products.models import Attribute, AttributeValue, ProductVariationOption
import json

class ProductAddView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.add_product")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = ProductForm()
        context['variation_formset'] = VariationFormSet(prefix='variations')
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        return context

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        variation_formset = VariationFormSet(request.POST, request.FILES, prefix='variations')

        print("form data:", request.POST)
        print("variation formset data:", variation_formset.data)

        if form.is_valid() and variation_formset.is_valid():
            try:
                with transaction.atomic():
                    # Save product first to establish the main object
                    product = form.save()

                    # Save the variations to get their PKs
                    variations = variation_formset.save(commit=False)
                    print("Variations before saving:", variations)
                    
                    for i, variation_form in enumerate(variation_formset.forms):
                        variation = variation_form.instance
                        if not variation_form.cleaned_data.get('DELETE', False):
                            variation.product = product
                            
                            # Generate cartesian_product_key from on-the-fly-attributes
                            attribute_data = request.POST.get(f'variations-{i}-on-the-fly-attributes', '')
                            if attribute_data:
                                attributes = json.loads(attribute_data)  # Parse JSON string
                                # key_parts = [attr["value"] for attr in attributes]  # Extract values (e.g., "Red", "Green")
                                # variation.cartesian_product_key = "/".join(key_parts)  # Set key (e.g., "Red" or "Green")
                                # variation.title = " / ".join(key_parts)  # Set title
                                
                                # # Generate a sample SKU
                                # sku_parts = [product.slug[:8].upper()] + [part[:3].upper() for part in key_parts]
                                # variation.sku = "-".join(sku_parts)

                            # Save the variation with the generated key and image

                            # Clear existing options before adding new ones
                            ProductVariationOption.objects.filter(variation=variation).delete()
                            
                            # Link attribute options
                            if attribute_data:
                                for attr in attributes:
                                    attributes = json.loads(attribute_data)  # Parse JSON string
                                    attr_name = attr["name"]
                                    attr_value = attr["value"]
                                    # Find or create attribute and value
                                    attribute, _ = Attribute.objects.get_or_create(name=attr_name)
                                    value, _ = AttributeValue.objects.get_or_create(attribute=attribute, value=attr_value)
                                    ProductVariationOption.objects.create(
                                        variation=variation,
                                        attribute=attribute,
                                        value=value
                                    )
                                    
                            variation.save()

                messages.success(request, f"Product '{product.name}' was added successfully.")
                return redirect('products')
            except Exception as e:
                messages.error(request, f"An error occurred while saving the product: {e}")
        
        messages.error(request, "Please correct the errors below.")

        print("Form errors:", form.errors)
        print("Variation formset errors:", variation_formset.errors)

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['variation_formset'] = variation_formset
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        return render(request, 'products/products_add.html', context)