from rest_framework import serializers

from account.api.serializers import AddressSerializer
from order.models import OrderItem, Order
from product.models import Product, ProductColor, FeatureValue, ProductStock, DiscountCode


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'quantity', 'price', 'total_price',
            'selected_color', 'selected_features'
        ]


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    selected_color = serializers.CharField()
    selected_features = serializers.DictField(child=serializers.CharField(), required=False)

    def validate(self, data):
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        color_name = data.get("selected_color")
        selected_features = data.get("selected_features", {})

        # Validate product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product.")

        # Validate color
        try:
            color = ProductColor.objects.get(name=color_name, product=product)
        except ProductColor.DoesNotExist:
            raise serializers.ValidationError("Invalid color for selected product.")

        # Convert feature values
        feature_values = []
        for feature_name, value in selected_features.items():
            try:
                fv = FeatureValue.objects.get(feature__name=feature_name, value=value)
                feature_values.append(fv)
            except FeatureValue.DoesNotExist:
                raise serializers.ValidationError(f"Feature '{feature_name}' with value '{value}' not found.")


        stock_qs = ProductStock.objects.filter(product=product, color=color)
        for fv in feature_values:
            stock_qs = stock_qs.filter(feature_values=fv)

        stock_item = stock_qs.first()
        if not stock_item:
            raise serializers.ValidationError("No stock found for this combination.")

        if stock_item.stock < quantity:
            raise serializers.ValidationError(f"Only {stock_item.stock} items available in stock.")

        return data


class CheckoutSerializer(serializers.Serializer):
    discount_code = serializers.CharField(required=False, allow_blank=True)

    def validate_discount_code(self, code):
        if not code:
            return None
        try:
            discount = DiscountCode.objects.get(code=code, active=True)
        except DiscountCode.DoesNotExist:
            raise serializers.ValidationError("Invalid discount code.")
        if not discount.is_valid():
            raise serializers.ValidationError("Discount code is expired or overused.")
        return discount

    def to_representation(self, instance):

        request = self.context['request']
        user = request.user
        order = instance

        return {
            "order_id": order.id,
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
            },
            "address": AddressSerializer(order.address).data if order.address else None,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total_price": item.total_price,
                }
                for item in order.items.all()
            ],
            "total_price": str(order.total_price),
            "shipping_cost": str(order.shipping_cost),
            "discount_amount": str(order.discount_amount),
            "final_price": str(order.final_price),
        }

    def update(self, instance, validated_data):
        discount = validated_data.get("discount_code")

        if discount:
            instance.discount_code = discount
            instance.discount_code.used_count += 1
            instance.discount_code.save()

        instance.status = 'processing'
        instance.is_paid = True
        instance.update_final_price()
        instance.save()

        return instance


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'created_at', 'status', 'final_price',
            'shipping_cost', 'discount_amount', 'items'
        ]
