from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant
from foods.models import Table
from foods.serializers import TableSerializer
from decimal import Decimal



UserModel = get_user_model()



class TenantSerializer(serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True)
    total_tables = serializers.IntegerField(write_only=True, required=False)
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 
            'tenant_name', 
            'has_hotel_feature',
            'gst_no',
            'total_tables',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'pin',
            'phone',
            'alt_phone',
            'email',
            'website',
            'logo',
            'tables',
            
            # GST Rates - all optional and flexible
            'restaurant_cgst',
            'restaurant_sgst',
            
            'hotel_cgst_lower',
            'hotel_sgst_lower',
            'hotel_cgst_upper',
            'hotel_sgst_upper',
            'hotel_gst_limit_margin',
            
            'service_cgst_lower',
            'service_sgst_lower',
            'service_cgst_upper',
            'service_sgst_upper',
            'service_gst_limit_margin',
            
            'subscription_from',
            'subscription_to',
            'subscription',
            'created_at',
            'modified_at',
            'modified_by'
        ]
        read_only_fields = ['created_at', 'modified_at', 'modified_by']

    def get_subscription(self, obj):
        from datetime import date
        if obj.subscription_from is None or obj.subscription_to is None:
            return None
        return obj.subscription_from <= date.today() <= obj.subscription_to

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