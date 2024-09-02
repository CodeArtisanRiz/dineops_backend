from rest_framework import serializers
from .models import Room
from .models import Booking
# from .models import Service, ServiceCategory
from accounts.models import User
from django.db import transaction
from .utils import get_or_create_user
import logging

logger = logging.getLogger(__name__)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'price', 'status', 'booking_id']

class BaseGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'dob', 'address']

# class GuestSerializer(BaseGuestSerializer):
#     class Meta(BaseGuestSerializer.Meta):
#         fields = BaseGuestSerializer.Meta.fields

class BookingSerializer(serializers.ModelSerializer):
    guests = BaseGuestSerializer(many=True)
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_date', 'from_date', 'to_date', 'status', 'scenario', 'guests', 'rooms', 'payment_method', 'total_amount', 'identification']

    def validate(self, data):
        guests_data = data.get('guests', [])
        rooms_data = data.get('rooms', [])
        scenario = data.get('scenario', 1)

        if scenario == 1 and len(guests_data) != 1:
            raise serializers.ValidationError("Scenario 1 requires exactly one guest.")
        elif scenario == 2 and len(guests_data) != len(rooms_data):
            raise serializers.ValidationError("Scenario 2 requires the number of guests to match the number of rooms.")
        elif scenario == 3 and len(guests_data) == 0:
            raise serializers.ValidationError("Scenario 3 requires at least one guest.")

        for room in rooms_data:
            if room.status != 'available':
                raise serializers.ValidationError(f"Room {room.id} is not available.")

        return data

    def create(self, validated_data):
        guests_data = validated_data.pop('guests')
        rooms_data = validated_data.pop('rooms')
        scenario = validated_data.get('scenario', 1)
        tenant = self.context['request'].user.tenant if not self.context['request'].user.is_superuser else validated_data.pop('tenant')
        total_amount = 0

        try:
            with transaction.atomic():
                booking = Booking.objects.create(tenant=tenant, **validated_data)
                logger.info("Booking created successfully")

                guest_users = []
                for guest_data in guests_data:
                    guest_user, created = get_or_create_user(guest_data)
                    guest_users.append(guest_user)

                    guest_total = 0
                    for room in rooms_data:
                        if room in guest_data.get('rooms', []):
                            room.status = 'occupied'
                            room.booking_id = booking
                            room.save()
                            guest_total += room.price

                    total_amount += guest_total

                    # Handle identification based on scenario
                    if scenario == 1 and not booking.identification:
                        booking.identification = guest_data.get('identification', "No ID Provided")
                    elif scenario == 2:
                        for room in guest_data.get('rooms', []):
                            booking.identification[room.id] = guest_data.get('identification', "No ID Provided")
                    elif scenario == 3:
                        if guest_user.id not in booking.identification:
                            booking.identification[guest_user.id] = guest_data.get('identification', "No ID Provided")

                booking.guests.set(guest_users)
                booking.rooms.set(rooms_data)  # Ensure rooms are set for the booking
                booking.total_amount = total_amount
                booking.save()
                logger.info("Booking finalized with total amount calculated")

            return booking
        except Exception as e:
            logger.error("Error during booking creation: %s", e)
            raise e