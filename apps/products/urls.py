from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.products.products.views_list import ProductListView, ProductsListJson
from apps.products.products.views_add import ProductAddView
from apps.products.products.views_update import ProductUpdateView

from apps.products.batches.views_add import BatchAddView
from apps.products.batches.views_update import BatchUpdateView
from apps.products.batches.views_delete import BatchDeleteView

from apps.products.categories.views_list import CategoryListView, CategoriesListJson
from apps.products.categories.views_add import CategoryCreateView
from apps.products.categories.views_update import CategoryUpdateView
from apps.products.categories.views_delete import CategoryDeleteView

from apps.products.departments.views_list import DepartmentListView, DepartmentsListJson
from apps.products.departments.views_add import DepartmentCreateView
from apps.products.departments.views_update import DepartmentUpdateView
from apps.products.departments.views_delete import DepartmentDeleteView

from apps.products.suppliers.views_list import SupplierListView, SuppliersListJson
from apps.products.suppliers.views_add import SupplierCreateView
from apps.products.suppliers.views_update import SupplierUpdateView
from apps.products.suppliers.views_delete import SupplierDeleteView

from apps.products.brands.views_list import BrandListView, BrandsListJson
from apps.products.brands.views_add import BrandCreateView
from apps.products.brands.views_update import BrandUpdateView
from apps.products.brands.views_delete import BrandDeleteView

from apps.transactions.transaction_delete.views import TransactionDeleteView

urlpatterns = [
    # Datatable APIs
    path('api/products/', ProductsListJson.as_view(), name='api_products'),
    path('api/categories/', CategoriesListJson.as_view(), name='api_categories'),
    path('api/departments/', DepartmentsListJson.as_view(), name='api_departments'),
    path('api/suppliers/', SuppliersListJson.as_view(), name='api_suppliers'),
    path('api/brands/', BrandsListJson.as_view(), name='api_brands'),

    # Products
    path(
        "products/list/",
        login_required(ProductListView.as_view(template_name="products/products_list.html")),
        name="products",
    ),
    path(
        "products/add/",
        login_required(ProductAddView.as_view(template_name="products/products_add.html")),
        name="products-add",
    ),
    path (
        "products/update/<uuid:pk>/",
        login_required(ProductUpdateView.as_view(template_name="products/products_update.html")),
        name="products-update",
    ),
    path (
        "products/delete/<int:pk>/",
        login_required(TransactionDeleteView.as_view()),
        name="products-delete",
    ),

    # Product Batches
    path (
        "batch/add/",
        login_required(BatchAddView.as_view(template_name="products/products_update.html")),
        name="batch-add",
    ),
    path (
        "batch/update/",
        login_required(BatchUpdateView.as_view(template_name="products/products_update.html")),
        name="batch-update",
    ),
    path (
        "batch/delete/<uuid:pk>/",
        login_required(BatchDeleteView.as_view(template_name="products/products_update.html")),
        name="batch-delete",
    ),
    
    # Product Categories
    path(
        "categories/list/",
        login_required(CategoryListView.as_view(template_name="categories/categories_list.html")),
        name="categories",
    ),
    path(
        "categories/add/",
        login_required(CategoryCreateView.as_view()),
        name="categories-add",
    ),
    path(
        "categories/update/<uuid:pk>/",
        login_required(CategoryUpdateView.as_view()),
        name="categories-update",
    ),
    path(
        "categories/delete/<uuid:pk>/",
        login_required(CategoryDeleteView.as_view()),
        name="categories-delete",
    ),

    # Product Departments
    path(
        "departments/list/",
        login_required(DepartmentListView.as_view()),
        name="departments",
    ),
    path(
        "departments/add/",
        login_required(DepartmentCreateView.as_view()),
        name="departments-add",
    ),
    path(
        "departments/update/<uuid:pk>/",
        login_required(DepartmentUpdateView.as_view()),
        name="departments-update",
    ),
    path(
        "departments/delete/<uuid:pk>/",
        login_required(DepartmentDeleteView.as_view()),
        name="departments-delete",
    ),

    # Product Suppliers
    path(
        "suppliers/list/",
        login_required(SupplierListView.as_view()),
        name="suppliers",
    ),
    path(
        "suppliers/add/",
        login_required(SupplierCreateView.as_view()),
        name="suppliers-add",
    ),
    path(
        "suppliers/update/<uuid:pk>/",
        login_required(SupplierUpdateView.as_view()),
        name="suppliers-update",
    ),
    path(
        "suppliers/delete/<uuid:pk>/",
        login_required(SupplierDeleteView.as_view()),
        name="suppliers-delete",
    ),

    # Product Brands
    path(
        "brands/list/",
        login_required(BrandListView.as_view()),
        name="brands",
    ),
    path(
        "brands/add/",
        login_required(BrandCreateView.as_view()),
        name="brands-add",
    ),
    path(
        "brands/update/<uuid:pk>/",
        login_required(BrandUpdateView.as_view()),
        name="brands-update",
    ),
    path(
        "brands/delete/<uuid:pk>/",
        login_required(BrandDeleteView.as_view()),
        name="brands-delete",
    ),

]
