from decimal import Decimal

from django.db import models
from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator
from account.models import User, Address
from product.models import Product, DiscountCode


# === Order Model ===
class Order(models.Model):
    """
    Represents a customer's order.

    Attributes:
        user (User): The customer who placed the order.
        address (Address): The shipping address selected by the user.
        created_at (datetime): The date and time when the order was created.
        updated_at (datetime): The date and time when the order was last updated.
        total_price (Decimal): The total price of the order before discounts.
        discount_code (DiscountCode, optional): The discount code applied to this order.
        discount_amount (Decimal): The total discount amount (calculated automatically).
        shipping_cost (Decimal): The calculated shipping cost based on weight.
        final_price (Decimal): The final payable amount after discount and shipping.
        is_paid (bool): Indicates whether the order has been paid for.
        status (str): The current status of the order.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
        verbose_name_plural = 'orders'
        db_table = 'order'

    from decimal import Decimal

    def calculate_shipping_cost(self):
        """ Calculates shipping cost based on total weight of the order. """
        total_weight = sum(item.get_total_weight() for item in self.items.all())
        if total_weight == 0:
            return Decimal('0')
        elif total_weight <= 5:
            return Decimal('5')
        elif total_weight <= 10:
            return Decimal('10')
        else:
            return Decimal(str(total_weight)) * Decimal('1.5')

    def apply_discount(self):
        """ Applies discount code if valid and updates discount amount. """
        if self.discount_code and self.discount_code.is_valid():
            self.discount_amount = self.discount_code.apply_discount(self.total_price)
        else:
            self.discount_amount = 0

    def update_final_price(self):
        """ Updates final price including shipping and discount. """
        self.apply_discount()
        self.shipping_cost = self.calculate_shipping_cost()
        self.final_price = max(self.total_price - self.discount_amount + self.shipping_cost, 0)

    def save(self, *args, **kwargs):
        """ Ensures that final price and shipping cost are updated before saving. """

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not is_new:
            self.update_final_price()
            super().save(update_fields=["shipping_cost", "final_price", "discount_amount"])

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


# === OrderItem Model ===
class OrderItem(models.Model):
    """
    Represents a single item within an order.

    Attributes:
        order (Order): The order to which this item belongs.
        product (Product): The product being purchased.
        quantity (int): The number of units of the product.
        price (Decimal): The price per unit of the product.
        total_price (Decimal): The total price for this item.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selected_color = models.CharField(max_length=100, blank=True, null=True)
    selected_features = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'order items'
        db_table = 'order_item'

    def save(self, *args, **kwargs):
        """ Ensures total price is updated before saving. """
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)
        self.order.update_final_price()

    def get_total_weight(self):
        """ Returns the total weight of this item in the order. """
        return self.quantity * self.product.weight

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


