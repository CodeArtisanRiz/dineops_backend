from rest_framework import serializers
from .models import FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'price', 'image','category', 'tenant']
        extra_kwargs = {
            'image': {'required': False},
            'tenant': {'required': False}
        }