from django.test import TestCase
from .models import Category, Product, Discount, DiscountCode, Image, ProductFeature
from django.utils.timezone import now, timedelta
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
# Create your tests here.


class CategoryModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.main_category = Category.objects.create(name="Electronics", slug="electronics")
        self.sub_category = Category.objects.create(name="Laptops", slug="laptops", parent=self.main_category)

    def test_category_creation(self):
        """Test if category is created successfully"""
        self.assertEqual(self.main_category.name, "Electronics")
        self.assertIsNone(self.main_category.parent)

    def test_subcategory_creation(self):
        """Test subcategory creation and relationship"""
        self.assertEqual(self.sub_category.parent, self.main_category)
        self.assertIn(self.sub_category, self.main_category.subcategories.all())

    def test_is_main_branch(self):
        """Test if is_main_branch() works correctly"""
        self.assertTrue(self.main_category.is_main_branch())
        self.assertFalse(self.sub_category.is_main_branch())

    def test_soft_delete(self):
        """Test soft delete functionality"""
        self.main_category.soft_delete()
        self.assertTrue(self.main_category.is_deleted)

    def test_restore(self):
        """Test restoring a soft-deleted category"""
        self.main_category.soft_delete()
        self.main_category.restore()
        self.assertFalse(self.main_category.is_deleted)




class ProductModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="Laptop",
            price=1000.00,
            stock=10,
            weight=2.5
        )

    def test_product_creation(self):
        """Test product creation"""
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.price, 1000.00)
        self.assertEqual(self.product.stock, 10)

    def test_product_slug_generation(self):
        """Test slug auto-generation"""
        self.assertIsNotNone(self.product.slug)

    def test_soft_delete(self):
        """Test soft delete functionality"""
        self.product.soft_delete()
        self.assertTrue(self.product.is_deleted)
        self.assertFalse(self.product.is_active)

    def test_restore(self):
        """Test restoring a soft-deleted product"""
        self.product.soft_delete()
        self.product.restore()
        self.assertFalse(self.product.is_deleted)
        self.assertTrue(self.product.is_active)





class DiscountModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(name="Laptop", price=1000.00, stock=5)
        self.discount = Discount.objects.create(
            product=self.product,
            value=10,
            discount_type="percent",
            start_date=now(),
            end_date=now() + timedelta(days=7)
        )

    def test_discount_creation(self):
        """Test discount creation"""
        self.assertEqual(self.discount.value, 10)
        self.assertEqual(self.discount.discount_type, "percent")

    def test_is_valid(self):
        """Test if discount is valid"""
        self.assertTrue(self.discount.is_valid())

    def test_apply_discount(self):
        """Test applying discount"""
        discounted_price = self.discount.apply_discount(self.product.price)
        self.assertEqual(discounted_price, 900.00)

    def test_invalid_discount_amount(self):
        """Test discount exceeding product price"""
        with self.assertRaises(ValueError):
            Discount.objects.create(product=self.product, value=1200, discount_type="amount")




class DiscountCodeModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.discount_code = DiscountCode.objects.create(
            code="TESTCODE",
            value=20,
            discount_type="percent",
            start_date=now(),
            end_date=now() + timedelta(days=7),
            max_uses=5
        )

    def test_discount_code_creation(self):
        """Test discount code creation"""
        self.assertEqual(self.discount_code.code, "TESTCODE")
        self.assertEqual(self.discount_code.value, 20)

    def test_is_valid(self):
        """Test if discount code is valid"""
        self.assertTrue(self.discount_code.is_valid())

    def test_apply_discount(self):
        """Test applying discount"""
        discounted_price = self.discount_code.apply_discount(1000)
        self.assertEqual(discounted_price, 800)

    def test_max_usage_exceeded(self):
        """Test exceeding max uses"""
        self.discount_code.used_count = 5
        self.assertFalse(self.discount_code.is_valid())


class ImageModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(name="Laptop", price=1000.00, stock=5)

        # Create a small test image
        image_file = BytesIO()
        image = PILImage.new("RGB", (100, 100), "blue")
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        self.image = Image.objects.create(
            product=self.product,
            file=SimpleUploadedFile("test.jpg", image_file.getvalue(), content_type="image/jpeg")
        )

    def test_image_creation(self):
        """Test image creation"""
        self.assertEqual(self.image.product, self.product)

    def test_invalid_image_format(self):
        """Test uploading an invalid image format"""
        with self.assertRaises(ValidationError):
            invalid_image = SimpleUploadedFile("test.txt", b"invalid data", content_type="text/plain")
            Image.objects.create(product=self.product, file=invalid_image)






class ProductFeatureTestCase(TestCase):
    """Tests for the ProductFeature model."""

    def setUp(self):
        """Set up test data before each test."""
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="iPhone 14",
            slug="iphone-14",
            stock=10,
            price=999.99,
            weight=0.5
        )

    def test_create_product_feature(self):
        """Test that a product feature can be created."""
        feature = ProductFeature.objects.create(
            product=self.product,
            name="Color",
            value="Black"
        )

        self.assertEqual(feature.product, self.product)
        self.assertEqual(feature.name, "Color")
        self.assertEqual(feature.value, "Black")
        self.assertEqual(ProductFeature.objects.count(), 1)

    def test_retrieve_product_features(self):
        """Test retrieving features of a product."""
        ProductFeature.objects.create(product=self.product, name="Color", value="Black")
        ProductFeature.objects.create(product=self.product, name="Storage", value="128GB")

        features = self.product.features.all()
        self.assertEqual(features.count(), 2)
        self.assertEqual(features.first().name, "Color")
        self.assertEqual(features.last().value, "128GB")

    def test_unique_together_constraint(self):
        """Test that a product cannot have duplicate feature names."""
        ProductFeature.objects.create(product=self.product, name="Color", value="Black")

        with self.assertRaises(Exception):
            ProductFeature.objects.create(product=self.product, name="Color", value="White")

    def test_feature_string_representation(self):
        """Test the string representation of ProductFeature."""
        feature = ProductFeature.objects.create(product=self.product, name="Brand", value="Apple")
        self.assertEqual(str(feature), "iPhone 14 - Brand: Apple")
