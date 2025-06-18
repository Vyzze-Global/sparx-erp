from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from .forms import DepartmentForm

class DepartmentCreateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.add_department"
    template_name = "departments/departments_add.html"  # Adjust path to your actual template

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = DepartmentForm()
        return context

    def post(self, request, *args, **kwargs):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect('departments')  # Adjust this name to your URL route name
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        return render(request, self.template_name, context)