from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from .forms import BrandForm  # Make sure you’ve imported the BrandForm

class BrandCreateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.add_brand"
    template_name = "brands/brands_add.html"  # Adjust this path based on your template structure

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = BrandForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand created successfully.")
            return redirect('brands')  # Adjust this redirect name based on your URL patterns
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        return render(request, self.template_name, context)