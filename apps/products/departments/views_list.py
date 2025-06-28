from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from web_project import TemplateLayout
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from apps.products.models import Department

class DepartmentListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.view_department",)
    template_name = "departments/departments_list.html" 

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class DepartmentsListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = ("products.view_department",)
    model = Department
    columns = ['control', 'name', 'description', 'actions']  # Simplified to match model
    order_columns = ['', 'name', 'description', '']  # Empty for control and actions
    max_display_length = 100

    def get_initial_queryset(self):
        return Department.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(slug__icontains=search) |
                Q(ref_1__icontains=search)
            ).distinct()
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'control': '',  # Placeholder for DataTable control
                'name': item.name or 'N/A',
                'description': item.description or 'N/A',
                'actions': '',  # Placeholder for actions
                'id': str(item.id)  # Include id in the JSON
            })
        return data

    def render_column(self, row, column):
        if column == 'control':
            return ''  # DataTable will handle the control column
        elif column == 'actions':
            return (
                f'<a href="/departments/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
                f'<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>'
                f'<div class="dropdown-menu dropdown-menu-end m-0">'
                f'<a href="/departments/view/{row.id}/" class="dropdown-item">View</a>'
                f'<a href="javascript:0;" class="dropdown-item delete-record" data-id="{row.id}">Delete</a>'
                f'</div>'
            )
        return super().render_column(row, column)