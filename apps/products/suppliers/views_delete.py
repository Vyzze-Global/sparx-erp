from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from apps.products.models import Supplier
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class SupplierDeleteView(PermissionRequiredMixin, View):
    permission_required = ("products.delete_supplier",)  # Adjust permission if needed

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, id=pk)

        # Confirm checkbox must be checked
        if not request.POST.get('objectDeletion'):
            messages.error(request, 'Please confirm deletion before submitting.')
            return redirect('suppliers-update', pk=pk)

        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('suppliers')