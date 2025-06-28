from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'total_price', 'final_price', 'is_paid']
    ordering = ['-created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['user__email', 'status']
    date_hierarchy = 'created_at'
    list_editable = ['status', 'is_paid']

    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Operator', 'Supervisor']).exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    ordering = ['order']
    list_filter = ['order', 'product']
    search_fields = ['order__id', 'product__name']

    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Operator', 'Supervisor']).exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Operator').exists() or request.user.is_superuser
