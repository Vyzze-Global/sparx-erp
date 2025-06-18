from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Category
from .forms import CategoryForm

class CategoryUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.change_category"
    template_name = "categories/categories_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        context['form'] = CategoryForm(instance=category)
        context['category'] = category
        return context

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f"Category '{category.name}' updated successfully.")
                    return redirect('categories')
            except Exception as e:
                messages.error(request, f"An error occurred while updating the category: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['category'] = category
        return render(request, self.template_name, context)