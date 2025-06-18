from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from web_project import TemplateLayout
from apps.products.models import Supplier

class SupplierListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.view_supplier",)
    template_name = "suppliers/suppliers_list.html"  # adjust to your template path

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class SuppliersListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = ("products.view_supplier",)
    model = Supplier
    columns = ['control', 'name', 'contact_person', 'phone_number', 'email', 'address', 'actions']
    order_columns = ['', 'name', 'contact_person', 'phone_number', 'email', 'address', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return Supplier.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search) |
                Q(address__icontains=search) |
                Q(website__icontains=search) |
                Q(bank_details__icontains=search) |
                Q(notes__icontains=search) |
                Q(remarks__icontains=search)
            ).distinct()
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'control': '',  # Placeholder for DataTable control
                'name': item.name or 'N/A',
                'contact_person': item.contact_person or 'N/A',
                'phone_number': item.phone_number or 'N/A',
                'email': item.email or 'N/A',
                'address': item.address or 'N/A',
                'actions': '',  # Placeholder for actions
                'id': str(item.id)  # Include id for actions
            })
        return data

    def render_column(self, row, column):
        if column == 'control':
            return ''  # DataTable will handle the control column
        elif column == 'actions':
            return (
                f'<a href="/suppliers/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
            )
        return super().render_column(row, column)