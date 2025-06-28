from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid


# === Custom User Manager ===
class UserManager(BaseUserManager):
    """ Custom manager for User model """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email is required"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# === User Model ===
class User(AbstractBaseUser, PermissionsMixin):
    """ Custom User model with email authentication & OTP login """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=11, unique=True, blank=True, null=True,
        validators=[RegexValidator(r'^09\d{9}$', _("Enter a valid phone number"))]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return self.email


# === Address Model ===
class Address(models.Model):
    """ Represents a user's address for shipping orders """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', _("Enter a valid 10-digit postal code"))]
    )
    no = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'address'
        verbose_name_plural = 'addresses'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['city']),
            models.Index(fields=['postal_code']),
        ]

    def __str__(self):
        return f"{self.province}, {self.city}, {self.street}, No. {self.no}"

    def save(self, *args, **kwargs):
        """ Ensures only one address is default """
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
