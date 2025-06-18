from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, AttributeValue, ProductVariation, Batch
from apps.products.products.forms import ProductForm, VariationFormSet
from apps.products.batches.forms import BatchForm


class BatchAddView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.add_batch")

    def post(self, request, *args, **kwargs):
        form = BatchForm(request.POST)
        variation_id = request.POST.get('variation_id')
        variation = get_object_or_404(ProductVariation, pk=variation_id)
        product = variation.product

        if form.is_valid():
            try:
                with transaction.atomic():
                    batch = form.save(commit=False)
                    batch.variation = variation
                    batch.save()
                    messages.success(request, f"Batch '{batch.batch_number}' added successfully.")
                    return redirect('products-update', pk=product.pk)
            except Exception as e:
                messages.error(request, f"An error occurred while adding the batch: {e}")
        else:
            messages.error(request, "Please correct the errors in the batch form.")

        context = TemplateLayout.init(self, {})
        context['form'] = ProductForm(instance=product)
        context['variation_formset'] = VariationFormSet(prefix='variations', instance=product)
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        context['product'] = product
        return render(request, 'products/products_update.html', context)