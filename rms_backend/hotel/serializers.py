from rest_framework import serializers
from .models import Room, Reservation, RoomHistory
from django.utils.dateparse import parse_datetime

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'status']

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user.tenant
        return super().create(validated_data)

class ReservationSerializer(serializers.ModelSerializer):
    check_in = serializers.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ', 'iso-8601'])
    check_out = serializers.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ', 'iso-8601'], required=False, allow_null=True)

    class Meta:
        model = Reservation
        fields = ['id', 'guest', 'room', 'check_in', 'check_out', 'tenant']

    def to_internal_value(self, data):
        if 'check_in' in data and isinstance(data['check_in'], str):
            data['check_in'] = parse_datetime(data['check_in'])
        if 'check_out' in data and isinstance(data['check_out'], str):
            data['check_out'] = parse_datetime(data['check_out'])
        return super().to_internal_value(data)

class RoomHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomHistory
        fields = ['id', 'reservation', 'room', 'start_date', 'end_date']