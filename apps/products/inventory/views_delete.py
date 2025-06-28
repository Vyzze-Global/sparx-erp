from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, ProductVariation, Inventory
from apps.products.products.forms import ProductForm, VariationFormSet

class InventoryDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.delete_inventory")

    def get(self, request, *args, **kwargs):
        inventory = get_object_or_404(Inventory, pk=kwargs['pk'])
        variation = inventory.variation
        product = variation.product
        try:
            with transaction.atomic():
                inventory.delete()
                messages.success(request, "Inventory entry deleted successfully.")
                return redirect('products-update', pk=product.pk)
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the inventory entry: {e}")

        context = TemplateLayout.init(self, {})
        context['form'] = ProductForm(instance=product)
        context['variation_formset'] = VariationFormSet(prefix='variations', instance=product)
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        context['product'] = product
        return render(request, 'products/products_update.html', context)