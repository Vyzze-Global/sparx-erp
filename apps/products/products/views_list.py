from django.views.generic import TemplateView
from web_project.template_helpers.theme import TemplateHelper
from web_project import TemplateLayout
from apps.products.models import ProductVariation
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from apps.products.models import ProductVariation
from django.contrib.auth.mixins import LoginRequiredMixin

class ProductListView(TemplateView):
    template_name = 'products/products_list_group.html'  # Update with your template path

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        TemplateHelper.map_context(context)
        context['page_title'] = 'Product Variations'
        return context

    def get_annotated_products(self):
        return ProductVariation.objects.select_related('product').order_by('product__name')

class ProductListJson(LoginRequiredMixin, BaseDatatableView):
    model = ProductVariation
    columns = [
        'id', 'id', 'product__name', 'variation_image', 'department', 'categories',
        'brand', 'standard_price', 'barcode', 'sku', 'stock_quantity', 'is_active', 'product__id', ''
    ]
    order_columns = [
        'id', 'id', 'product__name', 'variation_image', 'department', 'categories',
        'brand', 'standard_price', 'barcode', 'sku', 'stock_quantity', 'is_active', 'product__id', ''
    ]
    max_display_length = 100

    def get_initial_queryset(self):
        return ProductVariation.objects.select_related(
            'product', 'product__brand', 'product__department'
        ).prefetch_related(
            'product__categories', 'product__supplier'
        )

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(product__name__icontains=search) |
                Q(title__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(product__categories__name__icontains=search) |
                Q(product__brand__name__icontains=search) |
                Q(product__department__name__icontains=search) |
                Q(product__id__icontains=search) |
                Q(product__supplier__name__icontains=search)
            ).distinct()
        return qs

    def render_column(self, row, column):
        if column == 'product__name':
            return row.product.name if row.product else 'N/A'
        elif column == 'variation_image':
            image = row.image.url if row.image else (row.product.featured_image.url if row.product and row.product.featured_image else None)
            return self.request.build_absolute_uri(image) if image else None
        elif column == 'department':
            return row.product.department.name if row.product and row.product.department else 'N/A'
        elif column == 'categories':
            categories = row.product.categories.all() if row.product else []
            return categories[0].name if categories else 'Uncategorized'
        elif column == 'brand':
            return row.product.brand.name if row.product and row.product.brand else 'No Brand'
        elif column == 'standard_price':
            return f'${row.standard_price:.2f}' if row.standard_price else 'N/A'
        elif column == 'barcode':
            return row.barcode or 'N/A'
        elif column == 'sku':
            return row.sku or 'N/A'
        elif column == 'stock_quantity':
            return row.stock_quantity if row.stock_quantity is not None else 0
        elif column == 'is_active':
            status = {
                True: {'title': 'Active', 'class': 'bg-label-success'},
                False: {'title': 'Inactive', 'class': 'bg-label-secondary'}
            }
            return f'<span class="badge {status[row.is_active]["class"]}">{status[row.is_active]["title"]}</span>'
        elif column == 'product__id':
            return str(row.product.id) if row.product else 'N/A'
        elif column == '':
            return (
                f'<a href="/products/edit/{row.product.id}/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>'
                f'<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>'
                f'<div class="dropdown-menu dropdown-menu-end m-0">'
                f'<a href="/products/variation/view/{row.id}/" class="dropdown-item">View</a>'
                f'<a href="javascript:0;" class="dropdown-item text-danger delete-record" data-id="{row.id}">Delete</a>'
                f'</div>'
            )
        return super().render_column(row, column)

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'id': str(item.id),
                'product_id': str(item.product.id) if item.product else 'N/A',
                'product_name': item.product.name if item.product else 'N/A',
                'title': item.title or item.sku or 'N/A',
                'sku': item.sku or 'N/A',
                'barcode': item.barcode or 'N/A',
                'standard_price': float(item.standard_price) if item.standard_price else None,
                'stock_quantity': item.stock_quantity if item.stock_quantity is not None else 0,
                'is_active': item.is_active,
                'variation_image': self.request.build_absolute_uri(item.image.url) if item.image else None,
                'product_image': self.request.build_absolute_uri(item.product.featured_image.url) if item.product and item.product.featured_image else None,
                'categories': [{'name': cat.name} for cat in item.product.categories.all()] if item.product else [],
                'brand': {'name': item.product.brand.name} if item.product and item.product.brand else None,
                'department': {'name': item.product.department.name} if item.product and item.product.department else None,
                'suppliers': [{'id': str(sup.id), 'name': sup.name} for sup in item.product.supplier.all()] if item.product else []
            })
        return data