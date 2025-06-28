from django.urls import path
from .views import CartPageView, CheckoutPageView, CustomerPanelView

urlpatterns = [
    path('cart/', CartPageView.as_view(), name='cart-page'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout-page'),
    path('panel/', CustomerPanelView.as_view(), name='panel-page'),

]
