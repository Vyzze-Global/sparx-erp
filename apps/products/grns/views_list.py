from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q, Count
from django_datatables_view.base_datatable_view import BaseDatatableView
from web_project import TemplateLayout
from apps.products.models import Category

class CategoryListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("products.view_category")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class CategoriesListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = ("products.view_category")
    model = Category
    columns = ['id', 'id', 'name', 'display_name', 'type__name', 'department__name', 'parent__name', 'hide', '']
    order_columns = ['id', '', 'name', 'display_name', 'type__name', 'department__name', 'parent__name', 'hide', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return Category.objects.select_related('type', 'department', 'parent').annotate(
            total_products=Count('product')
        )

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(display_name__icontains=search) |
                Q(type__name__icontains=search) |
                Q(department__name__icontains=search) |
                Q(parent__name__icontains=search)
            ).distinct()
        return qs

    def render_column(self, row, column):
        if column == 'type__name':
            return row.type.name if row.type else 'N/A'
        elif column == 'department__name':
            return row.department.name if row.department else 'N/A'
        elif column == 'parent__name':
            return row.parent.name if row.parent else 'None'
        elif column == 'hide':
            return 'Hidden' if row.hide else 'Visible'
        elif column == '':
            return (
                f'<a href="/categories/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
                f'<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>'
                f'<div class="dropdown-menu dropdown-menu-end m-0">'
                f'<a href="/categories/view/{row.id}/" class="dropdown-item">View</a>'
                f'<a href="javascript:0;" class="dropdown-item delete-record" data-id="{row.id}">Delete</a>'
                f'</div>'
            )
        return super().render_column(row, column)

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'id': str(item.id),
                'name': item.name,
                'display_name': item.display_name,
                'type': {'name': item.type.name} if item.type else None,
                'department': {'name': item.department.name} if item.department else None,
                'parent': {'name': item.parent.name} if item.parent else None,
                'total_products': item.total_products,
                'hide': item.hide,
                'image': self.request.build_absolute_uri(item.image.url) if item.image and hasattr(item.image, 'url') else None
            })
        return data