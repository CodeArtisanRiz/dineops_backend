# Import necessary modules
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant

# Get the custom User model
UserModel = get_user_model()

# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'tenant', 'is_tenant_admin']

# Serializer for Tenant model
class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'  # Include all fields from the Tenant model