from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from apps.products.models import Brand
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class BrandDeleteView(PermissionRequiredMixin, View):
    permission_required = ("products.delete_brand",)

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)

        if not request.POST.get('objectDeletion'):
            messages.error(request, 'Please confirm deletion before submitting.')
            return redirect('brands-update', pk=pk)

        brand.delete()
        messages.success(request, 'Brand deleted successfully.')
        return redirect('brands')