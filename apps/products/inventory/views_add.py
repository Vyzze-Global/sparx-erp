from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, ProductVariation, Inventory, Batch
from apps.products.products.forms import ProductForm, VariationFormSet
from apps.products.inventory.forms import InventoryForm  # You should create this form

class InventoryAddView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.add_inventory")

    def post(self, request, *args, **kwargs):
        form = InventoryForm(request.POST)
        variation_id = request.POST.get('variation_id')
        batch_id = request.POST.get('batch_id')
        variation = get_object_or_404(ProductVariation, pk=variation_id)
        product = variation.product
        batch = None

        if batch_id:
            batch = get_object_or_404(Batch, pk=batch_id)

        print("Inventory form data:", request.POST)
        print("Variation:", variation)

        if form.is_valid():
            try:
                with transaction.atomic():
                    inventory = form.save(commit=False)
                    inventory.variation = variation
                    inventory.batch = batch
                    inventory.save()
                    messages.success(request, "Inventory added successfully.")
                    return redirect('products-update', pk=product.pk)
            except Exception as e:
                messages.error(request, f"An error occurred while adding inventory: {e}")
                return redirect('products-update', pk=product.pk)
        else:
            messages.error(request, "Please correct the errors in the inventory form.")
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")
            
            context = TemplateLayout.init(self, {})
            context['form'] = ProductForm(instance=product)
            context['variation_formset'] = VariationFormSet(prefix='variations', instance=product)
            context['attributes'] = Attribute.objects.prefetch_related('values').all()
            context['product'] = product
            context['inventory_form'] = form  # Add form with errors to pass to modal
            return render(request, 'products/products_update.html', context)
