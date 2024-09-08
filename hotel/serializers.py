from rest_framework import serializers
from .models import Room, ServiceCategory, Service
# , Booking
# from accounts.models import User
# from django.db import transaction
# from .utils import get_or_create_user
import logging
from datetime import date  # Add this import

logger = logging.getLogger(__name__)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'price', 'description', 'images', 'status']

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'sub_category', 'description', 'status']

class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'price']

# class BaseGuestSerializer(serializers.ModelSerializer):
#     identification = serializers.ListField(child=serializers.URLField(), required=False)
#     nationality = serializers.CharField(required=False, allow_blank=True)
#     coming_from = serializers.CharField(required=False, allow_blank=True)
#     going_to = serializers.CharField(required=False, allow_blank=True)
#     cform = serializers.JSONField(required=False)

#     class Meta:
#         model = User
#         fields = [
#             'id', 'first_name', 'last_name', 'phone', 'dob', 'address', 
#             'identification', 'nationality', 'coming_from', 'going_to', 'cform'
#         ]



# class BookingSerializer(serializers.ModelSerializer):
#     guests = BaseGuestSerializer(many=True, required=False)  # Make guests optional
#     rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
#     room_details = serializers.JSONField()

#     class Meta:
#         model = Booking
#         fields = [
#             'id', 'booking_date', 'status', 'scenario', 'guests', 
#             'rooms', 'total_amount_per_booking', 'room_details'
#         ]

#     def validate(self, data):
#         guests_data = data.get('guests', [])
#         rooms_data = data.get('rooms', [])
#         scenario = data.get('scenario', 1)
#         room_details = data.get('room_details', [])

#         if scenario == 1 and len(guests_data) != 1:
#             raise serializers.ValidationError("Scenario 1 requires exactly one guest.")
#         elif scenario == 2 and len(guests_data) != len(rooms_data):
#             raise serializers.ValidationError("Scenario 2 requires the number of guests to match the number of rooms.")
#         elif scenario == 3 and len(guests_data) == 0:
#             raise serializers.ValidationError("Scenario 3 requires at least one guest.")

#         for room in rooms_data:
#             if room.status != 'available':
#                 raise serializers.ValidationError(f"Room {room.id} is not available.")
#             for period in room.booked_periods:
#                 for detail in room_details:
#                     if room.room_number == detail['room_number']:
#                         from_date = detail.get('from_date')
#                         to_date = detail.get('to_date')
#                         if from_date >= to_date:
#                             raise serializers.ValidationError(f"to_date must be after from_date for room {detail['room_number']}.")
#                         if (from_date <= period['to_date'] and to_date >= period['from_date']):
#                             raise serializers.ValidationError(f"Room {room.id} is already booked for the requested date range.")

#         return data

#     def create(self, validated_data):
#         guests_data = validated_data.pop('guests', [])
#         rooms_data = validated_data.pop('rooms')
#         room_details = validated_data.pop('room_details')
#         scenario = validated_data.get('scenario', 1)
#         tenant = self.context['request'].user.tenant if not self.context['request'].user.is_superuser else validated_data.pop('tenant')
#         total_amount_per_booking = 0

#         logger.debug(f"Creating booking with data: {validated_data}")
#         logger.debug(f"Guests data: {guests_data}")
#         logger.debug(f"Rooms data: {rooms_data}")
#         logger.debug(f"Room details: {room_details}")

#         try:
#             with transaction.atomic():
#                 booking = Booking.objects.create(tenant=tenant, **validated_data)
#                 logger.info("Booking created successfully")

#                 guest_users = []
#                 for guest_data in guests_data:
#                     guest_user, created = get_or_create_user(guest_data, tenant)
#                     guest_users.append(guest_user)

#                 for room in rooms_data:
#                     for detail in room_details:
#                         if room.room_number == detail['room_number']:
#                             room.booked_periods.append({
#                                 'booking_id': booking.id,
#                                 'from_date': detail['from_date'],  # Assuming from_date is already a string
#                                 'to_date': detail['to_date']  # Assuming to_date is already a string
#                             })
#                             room.save()

#                 for room_detail in room_details:
#                     total_amount = float(room_detail.get('total_amount', 0))
#                     total_amount_per_booking += total_amount

#                     # Process opted services
#                     opted_services = room_detail.get('opted_services', [])
#                     for service in opted_services:
#                         service_obj = Service.objects.get(id=service['id'])
#                         service['name'] = service_obj.name
#                         service['category'] = service_obj.category.name
#                         service['price'] = str(service_obj.price)

#                     # Assign guests to room details
#                     room_guests = []
#                     for guest in guests_data:
#                         guest_user = next((gu for gu in guest_users if gu.phone == guest['phone']), None)
#                         if guest_user:
#                             room_guests.append({
#                                 'id': guest_user.id,
#                                 'first_name': guest_user.first_name,
#                                 'last_name': guest_user.last_name,
#                                 'phone': guest_user.phone,
#                                 'dob': guest_user.dob.isoformat() if isinstance(guest_user.dob, date) else guest_user.dob,  # Convert date to string if it's a date object
#                                 'address': guest_user.address,
#                                 'identification': guest.get('identification', []),  # Use identification from guest_data
#                                 'nationality': guest.get('nationality', ''),
#                                 'coming_from': guest.get('coming_from', ''),
#                                 'going_to': guest.get('going_to', ''),
#                                 'cform': guest.get('cform', {})
#                             })
#                     room_detail['guests'] = room_guests

#                 booking.guests.set(guest_users)
#                 booking.rooms.set(rooms_data)
#                 booking.room_details = room_details
#                 booking.total_amount_per_booking = total_amount_per_booking
#                 booking.save()
#                 logger.info("Booking finalized with total amount calculated")

#             return booking
#         except Exception as e:
#             logger.error("Error during booking creation: %s", e)
#             logger.debug(f"Booking data: {validated_data}")
#             logger.debug(f"Guests data: {guests_data}")
#             logger.debug(f"Rooms data: {rooms_data}")
#             logger.debug(f"Room details: {room_details}")
#             raise e

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation.pop('guests', None)  # Remove guests from the root level
#         return representation

# class AddServiceToRoomSerializer(serializers.Serializer):
#     booking_id = serializers.IntegerField()
#     room_id = serializers.IntegerField()
#     service_id = serializers.IntegerField()

#     def validate(self, data):
#         booking_id = data.get('booking_id')
#         room_id = data.get('room_id')
#         service_id = data.get('service_id')

#         try:
#             booking = Booking.objects.get(id=booking_id)
#         except Booking.DoesNotExist:
#             raise serializers.ValidationError("Booking does not exist.")

#         try:
#             room = Room.objects.get(id=room_id)
#         except Room.DoesNotExist:
#             raise serializers.ValidationError("Room does not exist.")

#         try:
#             service = Service.objects.get(id=service_id)
#         except Service.DoesNotExist:
#             raise serializers.ValidationError("Service does not exist.")

#         data['booking'] = booking
#         data['room'] = room
#         data['service'] = service

#         return data

#     def save(self):
#         booking = self.validated_data['booking']
#         room = self.validated_data['room']
#         service = self.validated_data['service']

#         for room_detail in booking.room_details:
#             if room_detail['room_number'] == room.room_number:
#                 if 'opted_services' not in room_detail:
#                     room_detail['opted_services'] = []
#                 room_detail['opted_services'].append({
#                     'id': service.id,
#                     'name': service.name,
#                     'category': service.category.name,
#                     'price': str(service.price)
#                 })
#                 break

#         booking.save()
#         return booking

# class RoomDetailUpdateSerializer(serializers.Serializer):
#     room_number = serializers.CharField(max_length=10)
#     check_in = serializers.DateTimeField(required=False)
#     check_out = serializers.DateTimeField(required=False)

# class RoomCheckOutSerializer(serializers.Serializer):
    # room_number = serializers.CharField(max_length=10)
    # check_out = serializers.DateTimeField(required=True)