from rest_framework import serializers
from .models import Room, Reservation
from accounts.models import User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    guest = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('status', 'actual_check_in', 'actual_check_out')

    def create(self, validated_data):
        mobile = self.context['request'].data.get('mobile')
        if mobile:
            guest, created = User.objects.get_or_create(
                username=mobile,
                defaults={'role': 'guest', 'password': 'guest-pass'}
            )
            validated_data['guest'] = guest
        
        room = validated_data['room']
        room.is_available = False
        room.save()
        
        return super().create(validated_data)