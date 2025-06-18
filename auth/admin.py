# from django.contrib import admin
# from .models import Profile

# # Register your models here.
# class Member(admin.ModelAdmin):
#     list_display = (
#         "user",
#         "email",
#         "is_verified",
#         "created_at",
#     )


# admin.site.register(Profile, Member)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserAccount, EmployeeProfile, CustomerProfile


@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin):
    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_verified', 'is_staff'
    )
    list_filter = ('user_type', 'is_active', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('email', 'phone_number', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'user_type')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'first_name', 'last_name', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'whatsapp', 'emp_code', 'is_verified', 'status', 'commission_rate')
    list_filter = ('status', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'mobile', 'whatsapp', 'emp_code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'whatsapp', 'is_verified', 'gender', 'age', 'loyalty_points')
    list_filter = ('gender', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'whatsapp')
    readonly_fields = ('created_at', 'updated_at')