from rest_framework import serializers
from django.db import models  # Import models from Django
from .models import Category, FoodItem, Table, Tenant
import json


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'tenant_name']  # Include necessary fields


class TableSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)  # Use PrimaryKeyRelatedField for tenant

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'occupied', 'tenant']  # Add 'tenant' to fields
        read_only_fields = ['tenant']  # Added 'tenant' to read_only_fields
    
    def create(self, validated_data):
        user = self.context['request'].user  # Get the current user from the request context
        if not user.is_superuser:
            validated_data['tenant'] = user.tenant  # Set tenant to user's tenant if not superuser
        else:
            tenant = validated_data.get('tenant')
            if tenant is None:
                raise serializers.ValidationError({"detail": "Superuser must provide a tenant."})
        
        tenant = validated_data['tenant']
        
        # Check if table_number is provided in the payload
        if 'table_number' not in validated_data:
            # Calculate the next available table number for the current tenant
            max_table_number = Table.objects.filter(tenant=tenant).aggregate(models.Max('table_number'))['table_number__max']
            validated_data['table_number'] = (max_table_number or 0) + 1
        else:
            # Ensure the provided table_number is unique within the tenant
            table_number = validated_data['table_number']
            if Table.objects.filter(tenant=tenant, table_number=table_number).exists():
                raise serializers.ValidationError({"detail": f"Table number {table_number} already exists for this tenant."})
        
        return super().create(validated_data)  # Call the parent create method

# Nested Nested CategorySerializer in FoodItem

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'tenant', 'name', 'description', 'image', 'status', 'created_at', 'modified_at']
#         read_only_fields = ['created_at', 'modified_at']
#         extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required

# class FoodItemSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)  # Nested serializer for category
#     category_id = serializers.PrimaryKeyRelatedField(
#         source='category',  # Use the 'category' field for the relationship
#         queryset=Category.objects.all(),
#         write_only=True,  # Accept this field in input but not output
#     )

#     class Meta:
#         model = FoodItem
#         fields = ['id', 'tenant', 'name', 'description', 'price', 'image', 'veg', 'category', 'category_id', 'status', 'created_at', 'modified_at', 'created_by', 'modified_by']
#         read_only_fields = ['created_at', 'modified_at', 'created_by', 'modified_by']  # Ensure these fields are read-only
#         extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required


# Removed Nested CategorySerializer but Retained category_id and catgeory_name
# Simplified response structure
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'tenant', 'name', 'description', 'image', 'status', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required

class FoodItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(  # Removed source argument
        queryset=Category.objects.all()  # Keep this as the primary key related field
    )
    category_name = serializers.SerializerMethodField() # Custom field to return the category name

    class Meta:
        model = FoodItem
        fields = ['id', 'tenant', 'name', 'description', 'price', 'image', 'veg', 'category',
                  'category_name', #returned category name
                  'status', 'created_at', 'modified_at', 'created_by', 'modified_by']
        read_only_fields = ['created_at', 'modified_at', 'created_by', 'modified_by']  # Ensure these fields are read-only
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required
    
    # Custom method to return the category name
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_image(self, obj):
        return json.loads(obj.image) if obj.image else []