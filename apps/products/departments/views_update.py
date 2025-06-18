from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import Department
from .forms import DepartmentForm

class DepartmentUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.change_department"
    template_name = "departments/departments_update.html"  # Ensure this template exists

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        department = get_object_or_404(Department, pk=self.kwargs['pk'])
        context['form'] = DepartmentForm(instance=department)
        context['department'] = department
        return context

    def post(self, request, *args, **kwargs):
        department = get_object_or_404(Department, pk=self.kwargs['pk'])
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f"Department '{department.name}' updated successfully.")
                    return redirect('departments')  # Ensure this named route exists
            except Exception as e:
                messages.error(request, f"An error occurred while updating the department: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        context['department'] = department
        return render(request, self.template_name, context)