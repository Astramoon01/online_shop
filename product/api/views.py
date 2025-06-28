from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from product.models import Category, Brand, Product, Discount, DiscountCode, ProductStock
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, ProductStockSerializer
)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        request = self.request

        queryset = Product.objects.filter(is_active=True, is_deleted=False)

        category_slug = request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    @action(detail=False)
    def featured(self, request):
        featured = self.get_queryset()[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stocks(self, request, slug=None):
        product = self.get_object()
        stocks = ProductStock.objects.filter(product=product).select_related('color', 'feature_value')
        serializer = ProductStockSerializer(stocks, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer

    @action(detail=True, url_path='products', methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True, is_deleted=False)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='slug/(?P<slug>[^/.]+)', methods=['get'])
    def get_by_slug(self, request, slug=None):
        category = get_object_or_404(Category, slug=slug, is_deleted=False)
        serializer = self.get_serializer(category)
        return Response(serializer.data)



class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
