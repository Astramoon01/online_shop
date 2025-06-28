from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import OrderItem, Order
from product.models import Product
from .serializers import CartAddSerializer, OrderItemSerializer, CheckoutSerializer, OrderListSerializer


class CartAddView(generics.CreateAPIView):
    serializer_class = CartAddSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']
        selected_color = serializer.validated_data.get('selected_color')
        selected_features = serializer.validated_data.get('selected_features', {})

        order, created = Order.objects.get_or_create(user=request.user, is_paid=False)


        if created or not order.pk:
            Order.objects.filter(id=order.id).update(total_price=0)


        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.get_final_price(),
            selected_color=selected_color,
            selected_features=selected_features,
        )


        order.total_price += order_item.total_price
        order.save()

        return Response(OrderItemSerializer(order_item).data, status=status.HTTP_201_CREATED)


class CartListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order = Order.objects.filter(user=self.request.user, is_paid=False).first()
        return order.items.all() if order else OrderItem.objects.none()


class CartItemDeleteView(generics.DestroyAPIView):
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        if item.order.user != request.user or item.order.is_paid:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        order = item.order
        order.total_price -= item.total_price
        item.delete()
        order.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = Order.objects.filter(user=request.user, is_paid=False).first()
        if not order:
            return Response({"detail": "No active cart found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CheckoutSerializer(order, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        order = Order.objects.filter(user=request.user, is_paid=False).first()
        if not order:
            return Response({"detail": "No active cart found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CheckoutSerializer(instance=order, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_paid=True).order_by('-created_at')

class ReceiptView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.is_paid:
            return Response({"detail": "Order already confirmed."}, status=status.HTTP_400_BAD_REQUEST)

        order.is_paid = True
        order.save()
        return Response({"message": "Order confirmed!"}, status=status.HTTP_200_OK)


class LatestOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = (
            Order.objects.filter(user=request.user, is_paid=True)
            .order_by("-created_at")
            .first()
        )
        if not order:
            return Response({"detail": "No recent paid order found."}, status=404)
        return Response({"id": order.id})