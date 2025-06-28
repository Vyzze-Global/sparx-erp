from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db import transaction

from web_project import TemplateLayout
from apps.products.models import PurchaseOrder
from apps.products.po.forms import PurchaseOrderForm, PurchaseOrderItemFormSet


class POUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.change_purchaseorder")
    template_name = "po/po_update.html"

    def get_context(self, **kwargs):
        po = get_object_or_404(PurchaseOrder, pk=kwargs.get("pk"))
        form = PurchaseOrderForm(instance=po)
        item_formset = PurchaseOrderItemFormSet(instance=po)
        context = TemplateLayout.init(self, {})

        context.update({
            "form": form,
            "po": po,
            "item_formset": item_formset
        })
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(**kwargs))


    def post(self, request, *args, **kwargs):
        po = get_object_or_404(PurchaseOrder, pk=kwargs.get("pk"))
        context = self.get_context(**kwargs)
        
        # Handle PO update
        if "po_update" in request.POST:
            form = PurchaseOrderForm(request.POST, instance=po)
            item_formset = PurchaseOrderItemFormSet(request.POST, instance=po)

            if form.is_valid() and item_formset.is_valid():
                try:
                    with transaction.atomic():
                        form.save()
                        item_formset.save()
                        messages.success(request, f"PO #{po.po_number} updated successfully.")
                        return redirect("po-update", pk=po.pk)
                except Exception as e:
                    messages.error(request, f"An error occurred while updating the PO: {e}")
            else:
                messages.error(request, "Please correct the errors below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
                for form in item_formset:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"Item {field.capitalize()}: {error}")

        elif "po_submit" in request.POST:
            po.status = 'submitted'
            po.save()
            messages.success(request, f"PO #{po.po_number} submitted successfully.")
            return redirect("po-update", pk=po.pk)
        
        elif "po_approve" in request.POST:
            po.status = 'approved'
            po.save()
            messages.success(request, f"PO #{po.po_number} approved successfully.")
            return redirect("po-update", pk=po.pk)


        
        return render(request, self.template_name, context)