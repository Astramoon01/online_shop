from django.urls import path
from .views import CartAddView, CartItemDeleteView, CartListView, CheckoutView, OrderListView, ReceiptView, \
    LatestOrderAPIView

urlpatterns = [
    path('cart/', CartAddView.as_view(), name='cart-add'),
    path('cart/items', CartListView.as_view(), name='cart-list'),
    path('cart/item/<int:pk>/', CartItemDeleteView.as_view(), name='cart-item-delete'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path("receipt/<int:pk>/", ReceiptView.as_view(), name="order-receipt"),
    path("orders/latest/", LatestOrderAPIView.as_view(), name="latest-order"),

]
