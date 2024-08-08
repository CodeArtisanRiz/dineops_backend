from rest_framework import serializers
from .models import FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'tenant', 'name', 'description', 'price', 'image', 'category', 'status', 'created_at', 'modified_at', 'created_by', 'modified_by']
        read_only_fields = ['created_at', 'modified_at', 'created_by', 'modified_by'] # Ensure these fields are read-only
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required