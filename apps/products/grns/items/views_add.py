# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from apps.products.models import GoodsReceiptNote, Batch, ProductVariation
from apps.products.grns.forms import GoodsReceiptNoteItemForm, GoodsReceiptNoteUpdateForm, GoodsReceiptNoteItemFormSet
from apps.products.batches.forms import BatchForm

class GRNItemAddView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.add_goodsreceiptnoteitem")
    template_name = "grns/grns_update.html"

    def post(self, request, *args, **kwargs):
        grn_item_form = GoodsReceiptNoteItemForm(request.POST)
        variation_id = request.POST.get('variation')
        variation = get_object_or_404(ProductVariation, pk=variation_id)
        grn_id = request.POST.get('grn')
        grn = get_object_or_404(GoodsReceiptNote, id=grn_id)

        if grn_item_form.is_valid():
            try:
                with transaction.atomic():
                    grn_item = grn_item_form.save(commit=False)
                    grn_item.variation = variation
                    grn_item.save()
                    messages.success(request, "GRN item added successfully.")
                    return redirect('grns-update', pk=grn.id)
            except Exception as e:
                messages.error(request, f"An error occurred while adding the entry: {e}")
                return redirect('grns-update', pk=grn.id)
        else:
            messages.error(request, "Please correct the errors in the batch form.")

        context = TemplateLayout.init(self, {})
        context['grn_item_form'] = grn_item_form
        context['grn'] = grn
        return render(request, self.template_name, context)

def handle_grn_item_add(request, grn_id, variation_id, context=None):
    """
    Handle GRN item addition with permission check.
    Args:
        request: The HTTP request object.
        grn_id: The ID of the GoodsReceiptNote.
        variation_id: The ID of the ProductVariation.
        context: Optional dict to update with form errors or data.
    Returns:
        dict: {
            'success': Boolean indicating if the operation was successful,
            'redirect': Optional redirect response if successful or on error,
            'form': The form instance if invalid,
            'context': Updated context if provided
        }
    """
    if not request.user.has_perm("products.add_goodsreceiptnoteitem"):
        raise PermissionDenied("You do not have permission to add GRN items.")

    grn = get_object_or_404(GoodsReceiptNote, id=grn_id)
    variation = get_object_or_404(ProductVariation, pk=variation_id) if variation_id else None
    grn_item_form = GoodsReceiptNoteItemForm(request.POST)

    if grn_item_form.is_valid():
        try:
            with transaction.atomic():
                grn_item = grn_item_form.save(commit=False)
                grn_item.grn = grn
                grn_item.variation = variation
                grn_item.save()
                messages.success(request, "GRN item added successfully.")
                return {
                    "success": True,
                    "redirect": redirect("grns-update", pk=grn.id),
                    "form": None,
                    "context": context
                }
        except Exception as e:
            messages.error(request, f"An error occurred while adding the GRN item: {e}")
            return {
                "success": False,
                "redirect": redirect("grns-update", pk=grn.id),
                "form": grn_item_form,
                "context": context
            }
    else:
        messages.error(request, "Please correct the errors in the GRN item form.")
        for field, errors in grn_item_form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")

    if context is not None:
        context["grn_item_form"] = grn_item_form
        context["grn"] = grn

    return {
        "success": False,
        "redirect": None,
        "form": grn_item_form,
        "context": context
    }