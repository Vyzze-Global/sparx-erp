from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, AttributeValue, ProductVariation, Batch
from apps.products.products.forms import ProductForm, VariationFormSet
from apps.products.batches.forms import BatchForm


class BatchDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.delete_batch")

    def get(self, request, *args, **kwargs):
        batch = get_object_or_404(Batch, pk=kwargs['pk'])
        product = batch.variation.product
        try:
            with transaction.atomic():
                batch.delete()
                messages.success(request, f"Batch deleted successfully.")
                return redirect('products-update', pk=product.pk)
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the batch: {e}")

        context = TemplateLayout.init(self, {})
        context['form'] = ProductForm(instance=product)
        context['variation_formset'] = VariationFormSet(prefix='variations', instance=product)
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        context['product'] = product
        return render(request, 'products/products_update.html', context)