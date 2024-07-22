# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import Tenant

# UserModel = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserModel
#         fields = ['id', 'username', 'email', 'tenant', 'is_tenant_admin', 'first_name', 'last_name', 'role', 'phone', 'address']
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant


UserModel = get_user_model()

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'password', 'email', 'tenant', 'is_tenant_admin', 'first_name', 'last_name', 'role', 'phone', 'address']
        extra_kwargs = {
            'password': {'write_only': True}
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