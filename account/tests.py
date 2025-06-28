from django.test import TestCase
from django.test import TestCase
from account.models import User, Address
from django.core.exceptions import ValidationError

# Create your tests here.

class UserModelTest(TestCase):

    def setUp(self):
        """ Set up test data """
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

    def test_create_user(self):
        """ Test if user is created successfully """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpass123"))
        self.assertFalse(self.user.is_staff)

    def test_create_superuser(self):
        """ Test creating a superuser """
        admin = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_invalid_email(self):
        """ Test user creation with an invalid email """
        with self.assertRaises(ValidationError):
            user = User(email="invalid-email", password="testpass")
            user.full_clean()  # This triggers Django's validation


class AddressModelTest(TestCase):

    def setUp(self):
        """ Set up a user and an address """
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

    def test_create_address(self):
        """ Test if address is created successfully """
        self.assertEqual(self.address.user, self.user)
        self.assertEqual(self.address.city, "Toronto")
        self.assertTrue(self.address.is_default)

    def test_only_one_default_address(self):
        """ Test that setting a new address as default removes previous default """
        new_address = Address.objects.create(
            user=self.user,
            province="Quebec",
            city="Montreal",
            street="456 Another St",
            postal_code="0987654321",
            no="10",
            is_default=True
        )
        self.address.refresh_from_db()
        self.assertFalse(self.address.is_default)
        self.assertTrue(new_address.is_default)

    def test_invalid_postal_code(self):
        """ Test validation for an invalid postal code """
        with self.assertRaises(ValidationError):
            address = Address(
                user=self.user,
                province="Ontario",
                city="Toronto",
                street="789 Some St",
                postal_code="12345",  # Invalid (not 10 digits)
                no="8"
            )
            address.full_clean()  # This triggers Django’s validation