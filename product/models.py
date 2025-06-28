from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import uuid
from django.core.validators import FileExtensionValidator


# === Category Model ===
class Category(models.Model):
    """
    Represents a hierarchical category system for products.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name_plural = 'categories'
        db_table = 'category'

    def get_absolute_api_url(self):
        return reverse('api:category-detail', args=[self.id])

    def is_main_branch(self):
        """ Checks if the category is a main branch (has no parent). """
        return self.parent is None  # True if it has no parent

    def get_all_branches(self):
        """ Returns all subcategories of this category if it's a main branch. """
        if self.is_main_branch():
            return self.subcategories.all()  # Returns all children categories
        return None  # If not main branch, returns None

    def show_related_branches(self):
        """
        Returns related branches:
        - If main branch: returns itself and its subcategories.
        - If not main branch: returns siblings and parent.
        """
        if self.is_main_branch():
            branch_list = list(self.get_all_branches())  # Get all subcategories
            branch_list.append(self)  # Add itself
        else:
            branch_list = list(self.parent.subcategories.all())  # Get siblings
            branch_list.append(self.parent)  # Add parent
        return branch_list

    def soft_delete(self):
        """ Soft delete: Marks the category as deleted instead of removing it from the database. """
        self.is_deleted = True
        self.save()

    def restore(self):
        """ Restores a soft-deleted category. """
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.name


# === Brand Model ===
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# === Product Model ===
class Product(models.Model):
    """
    Represents a product available in the store.

    Attributes:
        category (Category): The category to which the product belongs.
        name (str): The name of the product.
        slug (str): A unique identifier for URLs.
        description (str, optional): A detailed description of the product.
        stock (int): The number of items available in stock.
        price (Decimal): The original price of the product.
        weight (Decimal): The weight of the product.
        image (ImageField, optional): The main image of the product.
        created (datetime): Timestamp when the product was created.
        updated (datetime): Timestamp when the product was last updated.
        is_active (bool): Determines if the product is available for purchase.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(max_length=1200, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to="product_images/%Y/%m/%d", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name_plural = 'products'
        db_table = 'product'

    def save(self, *args, **kwargs):
        """ Generates a unique slug if not provided and ensures no duplicates. """
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_api_url(self):
        return reverse('api:product-detail', args=[self.id])

    def get_final_price(self):
        """ Calculates the final price after applying the discount. """
        if hasattr(self, 'discount') and self.discount.is_valid():
            return self.discount.apply_discount(self.price)
        return self.price

    def soft_delete(self):
        """ Soft delete: Marks the product as deleted instead of removing it. """
        self.is_deleted = True
        self.is_active = False
        self.save()

    def restore(self):
        """ Restores a soft-deleted product. """
        self.is_deleted = False
        self.is_active = True
        self.save()

    def __str__(self):
        return self.name

class Feature(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'product_feature'
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'

    def __str__(self):
        return self.name


class FeatureValue(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    color_swatch = models.ImageField(upload_to='features/swatches/', null=True, blank=True)
    hex_code = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        db_table = 'product_feature_value'
        verbose_name = 'Feature Value'
        verbose_name_plural = 'Feature Values'
        unique_together = ('feature', 'value')

    def __str__(self):
        return f"{self.feature.name}: {self.value}"


class ProductFeature(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='features')
    feature_value = models.ForeignKey(FeatureValue, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_product_feature'
        verbose_name = 'Product Feature'
        verbose_name_plural = 'Product Features'
        unique_together = ('product', 'feature_value')

    def __str__(self):
        return f"{self.product.name} - {self.feature_value}"

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        db_table = 'product_color'
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='stock_items')
    feature_values = models.ManyToManyField(FeatureValue, related_name='stock_items')
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_stock'
        verbose_name = 'Product Stock'
        verbose_name_plural = 'Product Stocks'
        unique_together = ('product', 'color')

    def __str__(self):
        features = ", ".join([f"{f.feature.name}: {f.value}" for f in self.feature_values.all()])
        return f"{self.product.name} - {self.color.name} - {features}"



# === Discount Model ===
class Discount(models.Model):
    """
    Represents a discount applied to a product.

    Attributes:
        product (Product): The product that receives the discount.
        value (Decimal): The discount amount (fixed or percentage).
        discount_type (str): Determines if the discount is a percentage or a fixed amount.
        start_date (datetime): The start date of the discount.
        end_date (datetime): The end date of the discount.
        active (bool): Determines if the discount is active.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Fixed Amount'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="discount")
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "discounts"
        db_table = "discount"

    def clean(self):
        """
        Validates discount rules:
        - Percentage discount should not exceed 100.
        - Fixed discount should not exceed product price.
        - Start date should be before end date.
        """
        if self.discount_type == 'percent' and self.value > 100:
            raise ValueError("Percentage discount cannot be greater than 100%")

        if self.discount_type == 'amount' and self.value > self.product.price:
            raise ValueError("Amount discount cannot exceed the product price")

        if self.start_date >= self.end_date:
            raise ValueError("End date must be after start date")

    def save(self, *args, **kwargs):
        """ Ensures discount rules are checked before saving. """
        self.clean()
        super().save(*args, **kwargs)

    def is_valid(self):
        """ Checks if the discount is still active and valid. """
        return self.active and self.start_date <= now() <= self.end_date

    def apply_discount(self, price):
        """ Applies the discount to the given price. """
        if not self.is_valid():
            return price

        if self.discount_type == 'percent':
            return price * (1 - (self.value / 100))
        elif self.discount_type == 'amount':
            return max(price - self.value, 0)
        return price

    def __str__(self):
        return f"Discount for {self.product.name} ({dict(self.DISCOUNT_TYPE_CHOICES).get(self.discount_type, 'Unknown')})"


# === DiscountCode Model ===
class DiscountCode(models.Model):
    """
    Represents a discount code that can be applied to an order.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4().hex[:10].upper())
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    min_order_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "discount codes"
        db_table = "discount_code"

    def clean(self):
        """ Validates discount code rules before saving. """
        if self.discount_type == 'percent' and self.value > 100:
            raise ValidationError("Percentage discount cannot be greater than 100%")

        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date")

        if self.used_count > self.max_uses:
            raise ValidationError("Used count cannot exceed max uses")

    def save(self, *args, **kwargs):
        """ Ensures clean method is called before saving. """
        self.clean()
        super().save(*args, **kwargs)

    def is_valid(self):
        """ Checks if the discount code is still valid (not expired and not overused). """
        return self.active and self.start_date <= now() <= self.end_date and self.used_count < self.max_uses

    def apply_discount(self, price):
        """ Applies the discount to the given order price. """
        if self.is_valid():
            if self.discount_type == 'percent':
                return price * (1 - (self.value / 100))
            elif self.discount_type == 'amount':
                return max(price - self.value, 0)
        return price

    def __str__(self):
        return f"Discount Code: {self.code}"


# === Image Model ===
def validate_image_size(image):
    max_size_kb = 2048  # 2 MB limit
    if image.size > max_size_kb * 1024:
        raise ValidationError(f"Image size should not exceed {max_size_kb} KB.")

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    file = models.ImageField(
        upload_to="product_images/%Y/%m/%d",
        default="product_images/default.jpg",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size
        ]
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]
        verbose_name_plural = 'images'
        db_table = 'image'

    def __str__(self):
        return f"Image for {self.product.name}"
