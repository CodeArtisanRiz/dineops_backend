from rest_framework import serializers
from .models import Booking, Room, Service, User
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'price']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'price', 'status']

class GuestSerializer(serializers.ModelSerializer):
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
    services = ServiceSerializer(many=True, required=False)
    identification = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'dob', 'address', 'rooms', 'services', 'identification']

class BookingSerializer(serializers.ModelSerializer):
    guests = GuestSerializer(many=True)
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)

    class Meta:
        model = Booking
        fields = ['booking_date', 'from_date', 'to_date', 'status', 'scenario', 'guests', 'rooms', 'payment_method', 'total_amount', 'identification']

    def create(self, validated_data):
        guests_data = validated_data.pop('guests')
        scenario = validated_data.get('scenario', 1)
        tenant = self.context['request'].user.tenant if not self.context['request'].user.is_superuser else validated_data.pop('tenant')
        total_amount = 0

        with transaction.atomic():
            booking = Booking.objects.create(tenant=tenant, **validated_data)
            logger.info("Booking created successfully")

            for guest_data in guests_data:
                rooms = guest_data.pop('rooms')
                services = guest_data.pop('services', [])
                identification = guest_data.pop('identification', None)

                # Create guest user
                guest_user = User.objects.create_user(
                    username=guest_data['phone'],
                    password=guest_data['dob'],  # Simplified for demo
                    role='guest',
                    **guest_data
                )
                booking.guests.add(guest_user)

                # Add rooms and services to guest
                for room in rooms:
                    room.status = 'occupied'
                    room.save()
                    booking.rooms.add(room)

                # Add services
                guest_total = sum(service['price'] for service in services)
                total_amount += sum(room.price for room in rooms) + guest_total

                # Handle identification based on scenario
                if scenario == 1 and not booking.identification:
                    booking.identification = identification or "No ID Provided"
                elif scenario == 2 and 'rooms' in guest_data:
                    for room in guest_data['rooms']:
                        booking.identification[room.id] = identification or "No ID Provided"
                elif scenario == 3:
                    if guest_user.id not in booking.identification:
                        booking.identification[guest_user.id] = identification or "No ID Provided"

                logger.info(f"Guest: {guest_user} added with rooms and services")

            booking.total_amount = total_amount
            booking.save()
            logger.info("Booking finalized with total amount calculated")

        return booking