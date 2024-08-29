from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant, Table


UserModel = get_user_model()

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'occupied', 'tenant']

class TenantSerializer(serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True)
    total_tables = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Tenant
        fields = [
            'id', 'tenant_name', 'domain_url', 'created_at', 'has_hotel_feature', 'gst_in', 'total_tables',
            'address_line_1', 'address_line_2', 'city', 'state', 'country', 'pin',
            'phone', 'alt_phone', 'email', 'website', 'logo_url', 'updated_at', 'tables'
        ]

    def create(self, validated_data):
        total_tables = validated_data.pop('total_tables', 0)
        tenant = super().create(validated_data)
        for i in range(1, total_tables + 1):
            Table.objects.create(tenant=tenant, table_number=i)
        return tenant

    def update(self, instance, validated_data):
        total_tables = validated_data.pop('total_tables', None)
        tenant = super().update(instance, validated_data)
        if total_tables is not None:
            current_count = tenant.tables.count()
            if total_tables > current_count:
                for i in range(current_count + 1, total_tables + 1):
                    Table.objects.create(tenant=tenant, table_number=i)
        return tenant
# class TenantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tenant
#         fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'password', 'email', 'tenant', 'first_name', 'last_name', 'role', 'phone', 'address']
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