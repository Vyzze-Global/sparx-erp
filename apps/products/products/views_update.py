from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Product, Attribute, AttributeValue, ProductVariation, ProductVariationOption
from apps.products.products.forms import ProductForm, VariationFormSet

class ProductUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.change_product")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        context['form'] = ProductForm(instance=product)
        context['variation_formset'] = VariationFormSet(prefix='variations', instance=product)
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        context['product'] = product
        return context

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        form = ProductForm(request.POST, request.FILES, instance=product)
        variation_formset = VariationFormSet(request.POST, request.FILES, prefix='variations', instance=product)

        print("form data:", request.POST)
        print("variation formset data:", variation_formset.data)

        if form.is_valid() and variation_formset.is_valid():
            try:
                with transaction.atomic():
                    # Save updated product
                    product = form.save()

                    # Save the variations
                    variations = variation_formset.save(commit=False)
                    print("Variations before saving:", variations)

                    for variation_form in variation_formset.forms:
                        variation = variation_form.instance
                        cleaned_data = variation_form.cleaned_data
                        # Skip empty forms marked for deletion or completely empty forms
                        if cleaned_data.get('DELETE') or not any(
                            cleaned_data.get(field) for field in ['title', 'standard_price', 'standard_sale_price', 'sku', 'barcode', 'image']
                        ):
                            continue

                        variation.product = product

                        # Save the variation
                        variation.save()

                        # Clear existing options (no new options created since on_the_fly_attributes is removed)
                        ProductVariationOption.objects.filter(variation=variation).delete()

                    # Handle deletions explicitly
                    for form in variation_formset.deleted_forms:
                        if form.instance.pk:  # Ensure the instance exists before deleting
                            form.instance.delete()

                    # Commit the formset save (if needed for other operations)
                    variation_formset.save_m2m()  # If there are any many-to-many fields

                    messages.success(request, f"Product '{product.name}' was updated successfully.")
                    return redirect('products')
            except Exception as e:
                messages.error(request, f"An error occurred while updating the product: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        print("Form errors:", form.errors)
        print("Variation formset errors:", variation_formset.errors)

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['variation_formset'] = variation_formset
        context['attributes'] = Attribute.objects.prefetch_related('values').all()
        context['product'] = product
        return render(request, self.template_name, context)