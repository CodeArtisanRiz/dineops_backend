from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'tenant', 'is_tenant_admin']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
