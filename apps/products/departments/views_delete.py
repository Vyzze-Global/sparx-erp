from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from apps.products.models import Department
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class DepartmentDeleteView(PermissionRequiredMixin, View):
    permission_required = ("products.delete_department",)

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        department = get_object_or_404(Department, id=pk)

        # Optionally check for a confirmation input (security measure)
        if not request.POST.get('objectDeletion'):
            messages.error(request, 'Please confirm deletion before submitting.')
            return redirect('departments-update', pk=pk)  # Make sure this route exists

        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('departments')  # Adjust to match your departments list view route