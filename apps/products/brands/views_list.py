from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from web_project import TemplateLayout
from apps.products.models import Brand

class BrandListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.view_brand",)
    template_name = "brands/brands_list.html"  # adjust to your template path

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class BrandsListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = ("products.view_brand",)
    model = Brand
    columns = ['control', 'name', 'logo', 'description', 'actions']
    order_columns = ['', 'name', 'logo', 'description', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return Brand.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            ).distinct()
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'control': '',  # Placeholder for DataTable control
                'name': item.name or 'N/A',
                'logo': self.request.build_absolute_uri(item.logo.url) if item.logo and hasattr(item.logo, 'url') else None,
                'description': item.description or 'N/A',
                'actions': '',  # Placeholder for actions
                'id': str(item.id)  # Include id for actions
            })
        return data

    def render_column(self, row, column):
        if column == 'control':
            return ''  # DataTable will handle the control column
        elif column == 'actions':
            return (
                f'<a href="/brands/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
            )
        return super().render_column(row, column)