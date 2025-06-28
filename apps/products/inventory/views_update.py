from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, ProductVariation, Inventory
from apps.products.products.forms import ProductForm, VariationFormSet
from apps.products.inventory.forms import InventoryUpdateForm


class InventoryUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.change_inventory")

    def post(self, request, *args, **kwargs):
        inventory_id = request.POST.get('inventory_id')
        inventory = get_object_or_404(Inventory, pk=inventory_id)
        variation = inventory.variation
        product = variation.product
        form = InventoryUpdateForm(request.POST, instance=inventory)

        print("Inventory form data:", request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, "Inventory updated successfully.")
                    return redirect('products-update', pk=product.pk)
            except Exception as e:
                messages.error(request, f"An error occurred while updating the inventory: {e}")
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
        return render(request, 'products/products_update.html', context)