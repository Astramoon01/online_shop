from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CartPageView(LoginRequiredMixin, TemplateView):
    template_name = 'cart/cart.html'

class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'cart/checkout.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class CustomerPanelView(LoginRequiredMixin, TemplateView):
    template_name = "home/panel.html"

class ReceiptPageView(LoginRequiredMixin, TemplateView):
    template_name = "cart/receipt.html"