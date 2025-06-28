from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db import transaction
from apps.products.utils import adjust_stock

from web_project import TemplateLayout
from apps.products.models import GoodsReceiptNote, PurchaseOrderItem
from .forms import GoodsReceiptNoteUpdateForm, GoodsReceiptNoteItemForm
from apps.products.grns.items.views_add import handle_grn_item_add
from apps.products.grns.items.views_update import handle_grn_item_update

class GRNUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.change_goodsreceiptnote")
    template_name = "grns/grns_update.html"

    def get_context(self, **kwargs):
        grn = get_object_or_404(GoodsReceiptNote, pk=kwargs.get("pk"))
        context = TemplateLayout.init(self, {})
        purchase_order_items = PurchaseOrderItem.objects.filter(purchase_order=grn.purchase_order)
        grn_items_by_po_item = {
            po_item.id: grn.items.filter(po_item=po_item) for po_item in purchase_order_items
        }
        context.update({
            "form": GoodsReceiptNoteUpdateForm(instance=grn),
            "grn": grn,
            "purchase_order_items": purchase_order_items,
            "grn_item_form": GoodsReceiptNoteItemForm(),
            "can_add_grn_item": self.request.user.has_perm("products.add_goodsreceiptnoteitem"),
            "grn_items_by_po_item": grn_items_by_po_item
        })
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(**kwargs))

    def post(self, request, *args, **kwargs):
        grn = get_object_or_404(GoodsReceiptNote, pk=kwargs.get("pk"))
        context = self.get_context(**kwargs)

        # Handle GRN update
        if "grn_update" in request.POST:
            form = GoodsReceiptNoteUpdateForm(request.POST, instance=grn)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        form.save()
                        messages.success(request, f"GRN #{grn.grn_number} updated successfully.")
                        return redirect("grns-update", pk=grn.pk)
                except Exception as e:
                    messages.error(request, f"An error occurred while updating the GRN: {e}")
            else:
                messages.error(request, "Please correct the errors below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
            context["form"] = form
            return render(request, self.template_name, context)

        # Handle GRN item addition
        elif "grn_item_add" in request.POST:
            result = handle_grn_item_add(
                request,
                grn_id=request.POST.get("grn"),
                variation_id=request.POST.get("variation"),
                context=context
            )
            if result["success"] or result["redirect"]:
                return result["redirect"]
            return render(request, self.template_name, context)
        
        # Handle GRN item update
        elif "grn_item_update" in request.POST:
            result = handle_grn_item_update(
                request,
                grn_item_id=request.POST.get("grn_item_id"),
                context=context
            )
            if result["success"] or result["redirect"]:
                return result["redirect"]
            return render(request, self.template_name, context)
        
        # GRN Approve
        elif "grn_approve" in request.POST:
            grn.status = 'approved'
            grn.save()
            messages.success(request, f"GRN #{grn.grn_number} approved successfully.")
            return redirect("grns-update", pk=grn.pk)
        
        # GRN Inspected
        elif "grn_inspected" in request.POST:
            grn.status = 'inspected'
            grn.save()
            messages.success(request, f"GRN #{grn.grn_number} marked inspected.")
            return redirect("grns-update", pk=grn.pk)
        
        # GRN Receive
        elif "grn_received" in request.POST:
            try:
                with transaction.atomic():
                    for item in grn.items.select_related('variation', 'batch').all():
                        if item.quantity_received and item.quantity_received > 0:
                            adjust_stock(
                                variation=item.variation,
                                warehouse=grn.warehouse,
                                batch=item.batch,
                                quantity=item.quantity_received,
                                transaction_type='purchase',
                                adjustment_type='in',
                                reference=grn,
                                remark=f"GRN #{grn.grn_number} received {'(Free Item)' if item.is_free_item else ''}"
                            )

                    grn.status = 'received'
                    grn.save()

                messages.success(request, f"GRN #{grn.grn_number} processed and stock updated.")
                return redirect("grns-update", pk=grn.pk)

            except Exception as e:
                messages.error(request, f"Error during GRN stock processing: {e}")
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)