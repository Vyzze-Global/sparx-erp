from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Brand
from .forms import BrandForm

class BrandUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.change_brand"
    template_name = "brands/brands_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        brand = get_object_or_404(Brand, pk=self.kwargs['pk'])
        context['form'] = BrandForm(instance=brand)
        context['brand'] = brand
        return context

    def post(self, request, *args, **kwargs):
        brand = get_object_or_404(Brand, pk=self.kwargs['pk'])
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f"Brand '{brand.name}' updated successfully.")
                    return redirect('brands')
            except Exception as e:
                messages.error(request, f"An error occurred while updating the brand: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['brand'] = brand
        return render(request, self.template_name, context)