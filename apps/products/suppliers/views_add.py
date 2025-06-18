from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from .forms import SupplierForm

class SupplierCreateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.add_supplier"
    template_name = "suppliers/suppliers_add.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = SupplierForm()
        return context

    def post(self, request, *args, **kwargs):
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier created successfully.")
            return redirect('suppliers')
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        return render(request, self.template_name, context)