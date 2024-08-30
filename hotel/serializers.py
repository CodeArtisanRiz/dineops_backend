from rest_framework import serializers
from .models import Room
from accounts.models import User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        # fields = ['id', 'room_number', 'room_type', 'price', 'is_available', 'description','status']
        fields = '__all__'