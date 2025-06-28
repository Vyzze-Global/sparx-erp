from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from apps.products.models import GoodsReceiptNoteItem

class GRNItemDeleteView(PermissionRequiredMixin, View):
    permission_required = ("products.delete_goodsreceiptnoteitem")

    def post(self, request, *args, **kwargs):
        grn_item = get_object_or_404(GoodsReceiptNoteItem, pk=kwargs['pk'])
        grn = grn_item.grn
        try:
            with transaction.atomic():
                grn_item.delete()
                messages.success(request, "GRN Item deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the GRN item: {e}")

        return redirect('grns-update', pk=grn.pk)