from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Supplier
from .forms import SupplierForm  # Ensure this is correctly defined and imported

class SupplierUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.change_supplier"
    template_name = "suppliers/suppliers_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        supplier = get_object_or_404(Supplier, pk=self.kwargs['pk'])
        context['form'] = SupplierForm(instance=supplier)
        context['supplier'] = supplier
        return context

    def post(self, request, *args, **kwargs):
        supplier = get_object_or_404(Supplier, pk=self.kwargs['pk'])
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f"Supplier '{supplier.name}' updated successfully.")
                    return redirect('suppliers')
            except Exception as e:
                messages.error(request, f"An error occurred while updating the supplier: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['supplier'] = supplier
        return render(request, self.template_name, context)