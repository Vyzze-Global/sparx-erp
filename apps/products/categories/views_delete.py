from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from apps.products.models import Category
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class CategoryDeleteView(PermissionRequiredMixin, View):
    permission_required = ("transactions.delete_category",)

    @method_decorator(csrf_protect)
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)

        # Optionally check for a confirmation input (security measure)
        if not request.POST.get('objectDeletion'):
            messages.error(request, 'Please confirm deletion before submitting.')
            return redirect('categories-update', pk=pk)

        category.delete()
        messages.success(request, 'Category Deleted')
        return redirect('categories')