from django.contrib import admin
from .models import User, Address

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone_number', 'is_active', 'is_staff', 'created_at']
    ordering = ['email']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    date_hierarchy = 'created_at'
    list_editable = ['is_active', 'is_staff']
    def has_module_permission(self, request):
        return request.user.groups.filter(name__in=['Operator', 'Supervisor']).exists() or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Operator', 'Supervisor']).exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'province', 'city', 'street', 'postal_code', 'is_default']
    ordering = ['user', 'province', 'city']
    list_filter = ['is_default', 'province', 'city']
    search_fields = ['user__email', 'province', 'city', 'street', 'postal_code']
    date_hierarchy = 'created_at'
    list_editable = ['is_default']
    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Operator', 'Supervisor']).exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser


