from django.shortcuts import render
from django.views.generic import TemplateView

from product.models import Category


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None, is_deleted=False)
        return context

class CategoryDetailView(TemplateView):
    template_name = 'product/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_slug'] = self.kwargs.get('slug')
        return context

class ProductDetailView(TemplateView):
    template_name = 'product/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context
