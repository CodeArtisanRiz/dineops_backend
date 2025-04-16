from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant, PhoneVerification  # Add PhoneVerification import
from foods.models import Table
from foods.serializers import TableSerializer
from decimal import Decimal

UserModel = get_user_model()

class TenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant
        fields = [
            'id', 'tenant_name', 'has_hotel_feature','logo','gst_no','fssai','hsn',
            'address_line_1', 'address_line_2', 'city', 'state', 'country','pin',
            'phone','alt_phone','email','website',
            # GST
            'gst_threshold',
            'room_cgst','room_sgst','room_cgst_premium', 'room_sgst_premium', 
            'food_cgst','food_sgst','food_cgst_premium', 'food_sgst_premium',
            
            'service_cgst','service_sgst',
            'created_at',
            'modified_at',
            'modified_by', 'created_at', 'modified_at', 'modified_by'
        ]
        read_only_fields = ['created_at', 'modified_at', 'modified_by']

    # def get_subscription(self, obj):
    #     from datetime import date
    #     if obj.subscription_from is None or obj.subscription_to is None:
    #         return None
    #     return obj.subscription_from <= date.today() <= obj.subscription_to

class UserSerializer(serializers.ModelSerializer):
    tenant_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = UserModel
        # fields = ['id', 'username', 'password', 'email', 'tenant', 'first_name', 'last_name', 'role', 'phone', 'address']
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'tenant': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = UserModel(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class PhoneVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerification
        fields = ['phone', 'verification_id', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at', 'verification_id']