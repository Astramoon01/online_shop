from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, Discount, DiscountCode, Image,
    ProductFeature, Brand, Feature, FeatureValue,
    ProductColor, ProductStock
)

# === Permission Mixin ===
class ProductAdminPermissionMixin:
    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Product Manager', 'Supervisor']).exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Product Manager').exists() or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Product Manager').exists() or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Product Manager').exists() or request.user.is_superuser


# === Admins with permission ===

@admin.register(Category)
class CategoryAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['name', 'parent', 'updated', 'is_deleted']
    ordering = ['name']
    list_filter = ['parent', 'is_deleted']
    search_fields = ['name']
    list_editable = ['is_deleted']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Product)
class ProductAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created']
    ordering = ['-created']
    list_filter = ['category', 'is_active', 'created']
    search_fields = ['name', 'description']
    date_hierarchy = 'created'
    list_editable = ['price', 'is_active']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Feature)
class FeatureAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(FeatureValue)
class FeatureValueAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['feature', 'value', 'hex_code', 'color_swatch_display']
    list_filter = ['feature']
    search_fields = ['value']

    def color_swatch_display(self, obj):
        if obj.hex_code:
            return format_html('<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>', obj.hex_code)
        elif obj.color_swatch:
            return format_html('<img src="{}" width="20" height="20" style="border:1px solid #ccc;" />', obj.color_swatch.url)
        return "-"
    color_swatch_display.short_description = "Swatch"


@admin.register(ProductFeature)
class ProductFeatureAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['product', 'feature_value']
    list_filter = ['feature_value__feature']
    search_fields = ['product__name', 'feature_value__value']


@admin.register(ProductColor)
class ProductColorAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['product', 'name', 'hex_code', 'color_display']
    list_filter = ['product']
    search_fields = ['name', 'product__name']

    def color_display(self, obj):
        if obj.hex_code:
            return format_html('<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc; border-radius: 4px;"></div>', obj.hex_code)
        return "-"
    color_display.short_description = "Color"


@admin.register(Brand)
class BrandAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Discount)
class DiscountAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['product', 'discount_type', 'value', 'start_date', 'end_date', 'active']
    ordering = ['-start_date']
    list_filter = ['discount_type', 'active']
    search_fields = ['product__name']
    list_editable = ['active', 'value']


@admin.register(DiscountCode)
class DiscountCodeAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'start_date', 'end_date', 'max_uses', 'used_count', 'active']
    ordering = ['-start_date']
    list_filter = ['discount_type', 'active']
    search_fields = ['code']
    list_editable = ['active', 'value', 'max_uses']


@admin.register(Image)
class ImageAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ['product', 'title', 'created']
    ordering = ['-created']
    search_fields = ['product__name', 'title']


@admin.register(ProductStock)
class ProductStockAdmin(ProductAdminPermissionMixin, admin.ModelAdmin):
    list_display = ('product', 'color', 'get_features', 'stock')
    filter_horizontal = ('feature_values',)

    def get_features(self, obj):
        return ", ".join(f"{fv.feature.name}: {fv.value}" for fv in obj.feature_values.all())
    get_features.short_description = "Features"
