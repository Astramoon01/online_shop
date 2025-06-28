from rest_framework import serializers
from account.models import User, Address
import random
from src.settings import redis_client
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils import timezone
import datetime


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'first_name', 'last_name', 'password')


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False #waiting till otp send and not active account till verify
        )

        otp_code = str(random.randint(100000, 999999))
        redis_client.setex(f"otp:{user.email}", 180, otp_code)
        print(f"OTP for {user.email}: {otp_code}")


        send_mail(
            subject="Your OTP Code - Maison Veloura",
            message=f"Hello {user.first_name},\n\nYour OTP code is: {otp_code}\nIt will expire in 3 minutes.",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        stored_otp = redis_client.get(f"otp:{email}")

        if not stored_otp:
            raise serializers.ValidationError("OTP expired or invalid")
        if stored_otp != otp:
            raise serializers.ValidationError("Incorrect OTP")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")

        user.is_active = True
        user.save()
        redis_client.delete(f"otp:{email}")
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account not verified")

        return data


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'province', 'city', 'street', 'postal_code', 'no', 'is_default']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)  # Ensure no duplicate
        if validated_data.get('is_default', False):
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return Address.objects.create(user=user, **validated_data)


class UserConfirmationSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()
    has_address = serializers.SerializerMethodField()
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'addresses', 'has_address']

    def get_addresses(self, obj):
        addresses = Address.objects.filter(user=obj, is_deleted=False)
        return AddressSerializer(addresses, many=True).data

    def get_has_address(self, obj):
        return Address.objects.filter(user=obj, is_deleted=False).exists()

    def update(self, instance, validated_data):
        phone_number = validated_data.get('phone_number')
        if phone_number:
            instance.phone_number = phone_number
            instance.save()
        return instance
