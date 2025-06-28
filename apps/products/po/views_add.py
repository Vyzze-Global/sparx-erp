from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from web_project import TemplateLayout
from apps.products.models import PurchaseOrder
from apps.products.po.forms import PurchaseOrderForm, PurchaseOrderItemFormSet

class POCreateView(PermissionRequiredMixin, TemplateView):
    template_name = 'po/po_add.html'
    permission_required = ("products.add_purchaseorder")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = PurchaseOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PurchaseOrderForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    purchase_order = form.save()

                    messages.success(request, f"Purchase Order #{purchase_order.po_number} created successfully.")
                    return redirect('po-update', pk=purchase_order.pk)
            except Exception as e:
                messages.error(request, f"An error occurred while saving the purchase order: {e}")
        else:
            messages.error(request, "Please correct the errors below.")

        context = TemplateLayout.init(self, {})
        context['form'] = form
        return render(request, self.template_name, context)