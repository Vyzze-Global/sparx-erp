from django.views.generic import TemplateView
from django.db.models import Sum
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout
from apps.products.models import Product
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class ProductListView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        TemplateHelper.map_context(context)
        return context

    def get_annotated_products(self):
        # Order products by name
        return Product.objects.select_related('brand', 'department').prefetch_related('categories').order_by('name')

class ProductsListJson(BaseDatatableView):
    model = Product
    columns = ['id', 'id', 'name', 'categories__name', 'in_stock', 'variations__sku', 'variations__standard_price', 'variations__stock_quantity', 'status', '']
    order_columns = ['id', '', 'name', 'categories__name', '', 'variations__sku', 'variations__standard_price', 'variations__stock_quantity', 'status', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return Product.objects.select_related('brand', 'department').prefetch_related('categories', 'variations')

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(categories__name__icontains=search) |
                Q(variations__sku__icontains=search) |
                Q(status__icontains=search)
            ).distinct()
        return qs

    def render_column(self, row, column):
        if column == 'categories__name':
            categories = row.categories.all()
            return categories[0].name if categories else 'Uncategorized'
        elif column == 'variations__sku':
            variations = row.variations.all()
            return variations[0].sku if variations else 'N/A'
        elif column == 'variations__standard_price':
            variations = row.variations.all()
            return f'${variations[0].standard_price:.2f}' if variations and variations[0].standard_price else 'N/A'
        elif column == 'variations__stock_quantity':
            variations = row.variations.all()
            return variations[0].stock_quantity if variations and variations[0].stock_quantity is not None else 0
        elif column == 'in_stock':
            return 'In_Stock' if row.in_stock else 'Out_of_Stock'
        elif column == '':
            return f'<a href="/products/edit/{row.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>' \
                   f'<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>' \
                   f'<div class="dropdown-menu dropdown-menu-end m-0">' \
                   f'<a href="/products/view/{row.id}/" class="dropdown-item">View</a>' \
                   f'<a href="javascript:0;" class="dropdown-item delete-record" data-id="{row.id}">Delete</a>' \
                   f'</div>'
        return super().render_column(row, column)

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'id': str(item.id),
                'name': item.name,
                'categories': [{'name': cat.name} for cat in item.categories.all()],
                'in_stock': item.in_stock,
                'sku': item.variations.first().sku if item.variations.exists() else 'N/A',
                'standard_price': item.variations.first().standard_price if item.variations.exists() and item.variations.first().standard_price else None,
                'stock_quantity': item.variations.first().stock_quantity if item.variations.exists() and item.variations.first().stock_quantity is not None else 0,
                'status': item.status,
                'brand': {'name': item.brand.name} if item.brand else None,
                'featured_image': self.request.build_absolute_uri(item.featured_image.url) if item.featured_image and hasattr(item.featured_image, 'url') else None
            })
        return data