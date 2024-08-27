# hotel/serializers.py

from rest_framework import serializers
from .models import Room
# , Reservation
from datetime import datetime
from django.db import transaction
from django.utils import timezone

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'price', 'type', 'status', 'bookings', 'past_bookings']

# class ReservationSerializer(serializers.ModelSerializer):
#     rooms = RoomSerializer(many=True, read_only=True)
#     room_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Room.objects.all(),
#         many=True,
#         write_only=True,
#         source='rooms'
#     )

#     class Meta:
#         model = Reservation
#         fields = ['id', 'guest_name', 'check_in_date', 'check_out_date', 'rooms', 'room_ids', 'booking_date']

#     def validate(self, data):
#         check_in = data.get('check_in_date')
#         check_out = data.get('check_out_date')
#         rooms = data.get('rooms')  # Access via source='rooms'

#         if check_in and check_out:
#             if check_in >= check_out:
#                 raise serializers.ValidationError("Check-out date must be after check-in date.")
#             if check_in < timezone.now():
#                 raise serializers.ValidationError("Check-in date cannot be in the past.")
        
#         if not rooms:
#             raise serializers.ValidationError("At least one room must be selected for reservation.")
#         return data

#     @transaction.atomic
#     def create(self, validated_data):
#         rooms = validated_data.pop('rooms')
#         guest_name = validated_data.get('guest_name')
#         check_in_date = validated_data.get('check_in_date')
#         check_out_date = validated_data.get('check_out_date')

#         # Perform validation on rooms
#         for room in rooms:
#             if room.status != 'available':
#                 raise serializers.ValidationError(f"Room {room.number} is not available for booking.")
#             for booking in room.bookings:
#                 existing_check_in = datetime.fromisoformat(booking['check_in_date'])
#                 existing_check_out = datetime.fromisoformat(booking['check_out_date'])
#                 if (check_in_date <= existing_check_out) and (check_out_date >= existing_check_in):
#                     raise serializers.ValidationError(
#                         f"Room {room.number} is already booked for the selected dates."
#                     )

#         # Create the reservation
#         reservation = Reservation.objects.create(**validated_data)

#         # Assign rooms to the reservation
#         reservation.rooms.set(rooms)

#         # Update room bookings
#         for room in rooms:
#             booking_detail = {
#                 'guest_name': guest_name,
#                 'check_in_date': check_in_date.isoformat(),
#                 'check_out_date': check_out_date.isoformat(),
#             }
#             room.bookings.append(booking_detail)
#             room.save()

#         return reservation
