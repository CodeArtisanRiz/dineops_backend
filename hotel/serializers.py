from rest_framework import serializers
from .models import Room, Booking
from accounts.models import User
from django.db import transaction
from .utils import get_or_create_user
import logging

logger = logging.getLogger(__name__)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'price', 'description', 'images', 'status', 'booked_periods']

class BaseGuestSerializer(serializers.ModelSerializer):
    identification = serializers.ListField(child=serializers.URLField(), required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'dob', 'address', 'identification']

class BookingSerializer(serializers.ModelSerializer):
    guests = BaseGuestSerializer(many=True)
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
    room_details = serializers.JSONField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_date', 'status', 'scenario', 'guests', 
            'rooms', 'total_amount_per_booking', 'room_details'
        ]

    def validate(self, data):
        guests_data = data.get('guests', [])
        rooms_data = data.get('rooms', [])
        scenario = data.get('scenario', 1)
        room_details = data.get('room_details', [])

        if scenario == 1 and len(guests_data) != 1:
            raise serializers.ValidationError("Scenario 1 requires exactly one guest.")
        elif scenario == 2 and len(guests_data) != len(rooms_data):
            raise serializers.ValidationError("Scenario 2 requires the number of guests to match the number of rooms.")
        elif scenario == 3 and len(guests_data) == 0:
            raise serializers.ValidationError("Scenario 3 requires at least one guest.")

        for room in rooms_data:
            if room.status != 'available':
                raise serializers.ValidationError(f"Room {room.id} is not available.")
            for period in room.booked_periods:
                for detail in room_details:
                    if room.room_number == detail['room_number']:
                        from_date = detail.get('from_date')
                        to_date = detail.get('to_date')
                        if from_date >= to_date:
                            raise serializers.ValidationError(f"to_date must be after from_date for room {detail['room_number']}.")
                        if (from_date <= period['to_date'] and to_date >= period['from_date']):
                            raise serializers.ValidationError(f"Room {room.id} is already booked for the requested date range.")

        return data

    def create(self, validated_data):
        guests_data = validated_data.pop('guests')
        rooms_data = validated_data.pop('rooms')
        room_details = validated_data.pop('room_details')
        scenario = validated_data.get('scenario', 1)
        tenant = self.context['request'].user.tenant if not self.context['request'].user.is_superuser else validated_data.pop('tenant')
        total_amount_per_booking = 0

        logger.debug(f"Creating booking with data: {validated_data}")
        logger.debug(f"Guests data: {guests_data}")
        logger.debug(f"Rooms data: {rooms_data}")
        logger.debug(f"Room details: {room_details}")

        try:
            with transaction.atomic():
                booking = Booking.objects.create(tenant=tenant, **validated_data)
                logger.info("Booking created successfully")

                guest_users = []
                for guest_data in guests_data:
                    guest_user, created = get_or_create_user(guest_data)
                    guest_users.append(guest_user)

                for room in rooms_data:
                    for detail in room_details:
                        if room.room_number == detail['room_number']:
                            room.booked_periods.append({
                                'booking_id': booking.id,
                                'from_date': detail['from_date'],
                                'to_date': detail['to_date']
                            })
                            room.save()

                for room_detail in room_details:
                    total_amount = float(room_detail.get('total_amount', 0))
                    total_amount_per_booking += total_amount

                booking.guests.set(guest_users)
                booking.rooms.set(rooms_data)
                booking.room_details = room_details
                booking.total_amount_per_booking = total_amount_per_booking
                booking.save()
                logger.info("Booking finalized with total amount calculated")

            return booking
        except Exception as e:
            logger.error("Error during booking creation: %s", e)
            logger.debug(f"Booking data: {validated_data}")
            logger.debug(f"Guests data: {guests_data}")
            logger.debug(f"Rooms data: {rooms_data}")
            logger.debug(f"Room details: {room_details}")
            raise e