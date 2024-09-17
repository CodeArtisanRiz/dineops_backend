from rest_framework import serializers
from .models import Category, FoodItem
import json
from .models import Table

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'occupied']
        read_only_fields = ['tenant']  # Added 'tenant' to read_only_fields
    
    def create(self, validated_data):
        user = self.context['request'].user  # Get the current user from the request context
        if not user.is_superuser:
            validated_data['tenant'] = user.tenant  # Set tenant to user's tenant if not superuser
        else:
            # Ensure tenant is taken from the payload if provided
            tenant = validated_data.get('tenant')
            if tenant is None:
                raise serializers.ValidationError("Superuser must provide a tenant.")
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