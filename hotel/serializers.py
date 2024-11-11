from rest_framework import serializers
from .models import Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, GuestDetails
import logging
from datetime import date
from accounts.models import User
from order.models import Order
from order.serializers import OrderSerializer

logger = logging.getLogger(__name__)

class RoomBookingSerializer(serializers.ModelSerializer):
    check_out_date = serializers.SerializerMethodField()
    checked_out_by = serializers.SerializerMethodField()
    check_in_details = serializers.SerializerMethodField()  # Existing field
    service_usages = serializers.SerializerMethodField()  # New field
    orders = serializers.SerializerMethodField()  # New field to include orders

    class Meta:
        model = RoomBooking
        fields = ['id', 'booking', 'room', 'start_date', 'end_date', 'is_active', 'check_in_details', 'check_out_date', 'checked_out_by', 'service_usages', 'orders']

    def get_check_out_date(self, obj):
        check_out = CheckOut.objects.filter(room_booking=obj).first()
        return check_out.check_out_date if check_out else None

    def get_checked_out_by(self, obj):
        check_out = CheckOut.objects.filter(room_booking=obj).first()
        return check_out.checked_out_by.id if check_out else None

    def get_check_in_details(self, obj):
        check_in = CheckIn.objects.filter(room_booking=obj).first()
        return CheckInDetailSerializer(check_in).data if check_in else None

    def get_service_usages(self, obj):
        # Fetch ServiceUsage instances related to this RoomBooking
        service_usages = ServiceUsage.objects.filter(room_id=obj, booking_id=obj.booking.id)
        return ServiceUsageSerializer(service_usages, many=True).data

    def get_orders(self, obj):
        # Ensure that the filtering is done using the correct fields
        orders = Order.objects.filter(booking_id=obj.booking.id, room_id=obj.room.id)
        return OrderSerializer(orders, many=True).data

class RoomSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'amenities', 'price', 'description', 'image', 'status', 'bookings']
        extra_kwargs = {'tenant': {'required': False}}

    def get_bookings(self, obj):
        active_bookings = obj.roombooking_set.filter(is_active=True)
        return [
            {
                "booking": RoomBookingSerializer(booking).data,
                "user": UserSerializer(booking.booking.guests.first()).data if booking.booking.guests.exists() else None
            }
            for booking in active_bookings
        ]

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'status', 'tenant']

class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'price', 'status', 'tenant']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address_line_1', 'address_line_2']

class BookingSerializer(serializers.ModelSerializer):
    rooms = RoomBookingSerializer(source='roombooking_set', many=True, read_only=True)
    guests = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    guest_detail = serializers.SerializerMethodField()  # New field for full user object

    class Meta:
        model = Booking
        fields = ['id', 'booking_date', 'status', 'total_amount', 'tenant', 'guests', 'guest_detail', 'rooms', 'id_card']
        extra_kwargs = {
            'id_card': {'required': False, 'allow_null': True}
        }

    def get_guest_detail(self, obj):
        # Return the full user object for each guest
        return UserSerializer(obj.guests.all(), many=True).data

    def create(self, validated_data):
        guests_data = validated_data.pop('guests', [])
        booking = super().create(validated_data)
        booking.guests.set(guests_data)
        return booking

    def update(self, instance, validated_data):
        guests_data = validated_data.pop('guests', [])
        instance = super().update(instance, validated_data)
        if guests_data:
            instance.guests.set(guests_data)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove the 'guests' field from the representation
        representation.pop('guests', None)
        return representation

class GuestDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestDetails
        fields = ['coming_from', 'going_to', 'purpose', 'guest_id', 'foreigner', 'c_form']

class GuestUserSerializer(serializers.ModelSerializer):
    guest_details = GuestDetailsSerializer(read_only=True)  # Include GuestDetails

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address_line_1', 'address_line_2', 'guest_details']

class CheckInSerializer(serializers.ModelSerializer):
    guests = GuestUserSerializer(many=True, read_only=True)

    class Meta:
        model = CheckIn
        fields = ['id', 'room_booking', 'check_in_date', 'checked_in_by', 'guests']

class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOut
        fields = ['id', 'room_booking', 'check_out_date', 'checked_out_by']

class ServiceUsageSerializer(serializers.ModelSerializer):
    service_name = serializers.SerializerMethodField()  # Existing field
    room_booking_id = serializers.IntegerField(write_only=True)  # Accept room_booking_id as input
    room_id = serializers.SerializerMethodField()  # New field for Room ID

    class Meta:
        model = ServiceUsage
        fields = ['id', 'booking_id', 'room_booking_id', 'room_id', 'service_id', 'service_name', 'usage_date']

    def get_service_name(self, obj):
        return obj.service_id.name  # Fetch the name of the service

    def get_room_id(self, obj):
        return obj.room_id.room.id  # Fetch the room ID from the RoomBooking

    def create(self, validated_data):
        # Extract room_booking_id from validated_data
        room_booking_id = validated_data.pop('room_booking_id')
        # Fetch the RoomBooking instance
        room_booking = RoomBooking.objects.get(id=room_booking_id)
        # Assign the RoomBooking instance to room_id
        validated_data['room_id'] = room_booking
        # Create the ServiceUsage instance
        return super().create(validated_data)

class CheckInDetailSerializer(serializers.ModelSerializer):
    guests = GuestUserSerializer(many=True, read_only=True)

    class Meta:
        model = CheckIn
        fields = ['id', 'room_booking', 'check_in_date', 'checked_in_by', 'guests']
