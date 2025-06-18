from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from .forms import CategoryForm

class CategoryCreateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.add_category"
    template_name = "categories/categories_add.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = CategoryForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('categories')
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        return render(request, self.template_name, context)