from rest_framework import serializers
from .models import Category, FoodItem
import json

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
    # image = serializers.SerializerMethodField()
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',  # Use the 'category' field for the relationship
        queryset=Category.objects.all()
    )
    category_name = serializers.SerializerMethodField() # Custom field to return the category name

    class Meta:
        model = FoodItem
        fields = ['id', 'tenant', 'name', 'description', 'price', 'image', 'veg', 'category_id',
                  'category_name', #returned category name
                  'status', 'created_at', 'modified_at', 'created_by', 'modified_by']
        read_only_fields = ['created_at', 'modified_at', 'created_by', 'modified_by']  # Ensure these fields are read-only
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required
    
    # Custom method to return the category name
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_image(self, obj):
        return json.loads(obj.image) if obj.image else []