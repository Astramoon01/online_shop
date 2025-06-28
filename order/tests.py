from decimal import Decimal

from django.test import TestCase

from account.models import User, Address
from order.models import Order, OrderItem
from product.models import Product, DiscountCode


# Create your tests here.
class OrderModelTest(TestCase):

    def setUp(self):
        """ Set up user, address, and order """
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.address = Address.objects.create(
            user=self.user,
            province="Ontario",
            city="Toronto",
            street="123 Main St",
            postal_code="1234567890",
            no="5",
            is_default=True
        )
        self.order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_price=Decimal("100.00"),
            is_paid=False,
            status="pending"
        )

    def test_create_order(self):
        """ Test order creation """
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.address, self.address)
        self.assertEqual(self.order.total_price, Decimal("100.00"))
        self.assertEqual(self.order.status, "pending")
        self.assertFalse(self.order.is_paid)

    def test_apply_discount(self):
        """ Test applying a discount code """
        discount_code = DiscountCode.objects.create(code="DISCOUNT10", discount_percentage=10)
        self.order.discount_code = discount_code
        self.order.apply_discount()
        self.order.save()
        self.assertEqual(self.order.discount_amount, Decimal("10.00"))  # 10% of 100

    def test_update_final_price(self):
        """ Test calculating final price after discount and shipping """
        self.order.update_final_price()
        self.assertGreaterEqual(self.order.final_price, 0)


class OrderItemModelTest(TestCase):

    def setUp(self):
        """ Set up user, product, order, and order item """
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.address = Address.objects.create(
            user=self.user,
            province="Ontario",
            city="Toronto",
            street="123 Main St",
            postal_code="1234567890",
            no="5",
            is_default=True
        )
        self.order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_price=Decimal("100.00"),
            is_paid=False,
            status="pending"
        )
        self.product = Product.objects.create(name="Laptop", price=Decimal("50.00"), weight=2.0)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal("50.00")
        )

    def test_create_order_item(self):
        """ Test order item creation """
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.total_price, Decimal("100.00"))

    def test_total_weight_calculation(self):
        """ Test if total weight calculation works correctly """
        total_weight = self.order_item.get_total_weight()
        self.assertEqual(total_weight, 4.0)  # 2 * 2kg

    def test_order_final_price_after_adding_item(self):
        """ Test if the order updates its final price when an item is added """
        self.order.refresh_from_db()
        self.assertEqual(self.order.final_price, Decimal("100.00"))  # Initial total price
