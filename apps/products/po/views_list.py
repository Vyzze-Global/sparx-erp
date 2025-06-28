from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from web_project import TemplateLayout
from apps.products.models import PurchaseOrder

class PurchaseOrderListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.view_purchaseorder")
    template_name = "po/po_list.html" 
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class PurchaseOrdersListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = ("products.view_purchaseorder")
    model = PurchaseOrder
    columns = ['id', 'id', 'po_number', 'supplier__name', 'warehouse__name', 'order_date', 'status', 'expected_delivery_date', 'total', '']
    order_columns = ['id', '', 'po_number', 'supplier__name', 'warehouse__name', 'order_date', 'status', 'expected_delivery_date', 'total', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return PurchaseOrder.objects.select_related('supplier', 'warehouse', 'approved_by')

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(po_number__icontains=search) |
                Q(supplier__name__icontains=search) |
                Q(warehouse__name__icontains=search) |
                Q(status__icontains=search)
            ).distinct()
        return qs

    def render_column(self, row, column):
        if column == 'supplier__name':
            return row.supplier.name if row.supplier else 'N/A'
        elif column == 'warehouse__name':
            return row.warehouse.name if row.warehouse else 'N/A'
        elif column == 'order_date':
            return row.order_date.strftime('%Y-%m-%d') if row.order_date else 'N/A'
        elif column == 'expected_delivery_date':
            return row.expected_delivery_date.strftime('%Y-%m-%d') if row.expected_delivery_date else 'N/A'
        elif column == 'status':
            return row.get_status_display()
        elif column == 'total':
            return f'${row.total:.2f}'
        elif column == '':
            return (
                f'<a href="/purchase-orders/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
                f'<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>'
                f'<div class="dropdown-menu dropdown-menu-end m-0">'
                f'<a href="/purchase-orders/view/{row.id}/" class="dropdown-item">View</a>'
                f'<a href="javascript:0;" class="dropdown-item delete-record" data-id="{row.id}">Delete</a>'
                f'</div>'
            )
        return super().render_column(row, column)

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'id': str(item.id),
                'po_number': item.po_number,
                'supplier': {'name': item.supplier.name} if item.supplier else None,
                'warehouse': {'name': item.warehouse.name} if item.warehouse else None,
                'order_date': item.order_date.strftime('%Y-%m-%d') if item.order_date else None,
                'status': item.get_status_display(),
                'expected_delivery_date': item.expected_delivery_date.strftime('%Y-%m-%d') if item.expected_delivery_date else None,
                'total': float(item.total),
                'approved_by': item.approved_by.get_full_name() if item.approved_by else None,
                'notes': item.notes
            })
        return data