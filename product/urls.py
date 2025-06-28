from django.urls import path
from .views import HomeView, CategoryDetailView, ProductDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
