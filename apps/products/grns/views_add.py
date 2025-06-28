from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from django.db import transaction
from .forms import GoodsReceiptNoteForm

class GRNCreateView(PermissionRequiredMixin, TemplateView):
    permission_required = "products.add_goodsreceiptnote"
    template_name = "po/po_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['form'] = GoodsReceiptNoteForm()
        return context

    def post(self, request, *args, **kwargs):
        form = GoodsReceiptNoteForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    grn = form.save()
                    messages.success(request, f"GRN #{grn.grn_number} created successfully.")
                    return redirect('grns-update', pk=grn.pk)
            except Exception as e:
                form.add_error(None, f"Error while creating GRN: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form.fields[field].label}: {error}")

        # Preserve consistent context for re-rendering
        context = TemplateLayout.init(self, {})
        context["form"] = form
        return render(request, self.template_name, context)