from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from web_project import TemplateLayout
from django.core.exceptions import PermissionDenied

from apps.products.grns.forms import GoodsReceiptNoteItemForm
from apps.products.models import GoodsReceiptNoteItem

class GRNItemUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.change_goodsreceiptnoteitem")
    template_name = "grns/grns_update.html"

    def post(self, request, *args, **kwargs):
        grn_item = get_object_or_404(GoodsReceiptNoteItem, pk=kwargs['pk'])
        form = GoodsReceiptNoteItemForm(request.POST, instance=grn_item)
        grn = grn_item.grn

        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_item = form.save()
                    messages.success(request, "GRN item updated successfully.")
                    return redirect('grns-update', pk=grn.id)
            except Exception as e:
                messages.error(request, f"Error updating GRN item: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

        context = TemplateLayout.init(self, {})
        context["grn_item_form"] = form
        context["grn"] = grn
        return render(request, self.template_name, context)
    
    
def handle_grn_item_update(request, grn_item_id, context=None):
    """
    Handle GRN item update with permission check.
    Args:
        request: The HTTP request object.
        grn_item_id: The ID of the GoodsReceiptNoteItem to update.
        context: Optional dict to update with form errors or data.
    Returns:
        dict: {
            'success': Boolean indicating if the operation was successful,
            'redirect': Optional redirect response if successful or on error,
            'form': The form instance if invalid,
            'context': Updated context if provided
        }
    """
    if not request.user.has_perm("products.change_goodsreceiptnoteitem"):
        raise PermissionDenied("You do not have permission to change GRN items.")

    grn_item = get_object_or_404(GoodsReceiptNoteItem, pk=grn_item_id)
    grn = grn_item.grn
    form = GoodsReceiptNoteItemForm(request.POST, instance=grn_item)

    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
                messages.success(request, "GRN item updated successfully.")
                return {
                    "success": True,
                    "redirect": redirect("grns-update", pk=grn.id),
                    "form": None,
                    "context": context
                }
        except Exception as e:
            messages.error(request, f"An error occurred while updating the GRN item: {e}")
            return {
                "success": False,
                "redirect": redirect("grns-update", pk=grn.id),
                "form": form,
                "context": context
            }
    else:
        messages.error(request, "Please correct the errors in the GRN item form.")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    if context is not None:
        context["grn_item_form"] = form
        context["grn"] = grn

    return {
        "success": False,
        "redirect": None,
        "form": form,
        "context": context
    }