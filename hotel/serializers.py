from rest_framework import serializers
from .models import Room, ServiceCategory, Service
import logging
from datetime import date  # Add this import

logger = logging.getLogger(__name__)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'price', 'description', 'image', 'status']
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required
        
class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'sub_category', 'description', 'status']

class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'price']