from rest_framework import serializers
from .models import Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, Billing, Payment
import logging
from datetime import date  # Add this import
from accounts.models import User  # Import User model

logger = logging.getLogger(__name__)

class RoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBooking
        fields = ['id', 'booking', 'room', 'start_date', 'end_date', 'status', 'is_active']

class RoomSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'price', 'description', 'image', 'status', 'bookings']
        extra_kwargs = {'tenant': {'required': False}}  # Make tenant not required

    def get_bookings(self, obj):
        active_bookings = obj.roombooking_set.filter(is_active=True)
        return RoomBookingSerializer(active_bookings, many=True).data

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'sub_category', 'description', 'status']

class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'price']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address']  # Include all necessary fields
        
class BookingSerializer(serializers.ModelSerializer):
    rooms = RoomBookingSerializer(source='roombooking_set', many=True, read_only=True)
    guests = UserSerializer(many=True, read_only=True)  # Use UserSerializer for guests

    class Meta:
        model = Booking
        fields = ['id', 'booking_date', 'status', 'total_amount', 'tenant', 'guests', 'rooms', 'id_card']
        extra_kwargs = {
            'id_card': {'required': False, 'allow_null': True}  # Allow null values
        }

class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ['id', 'room_booking', 'check_in_date', 'checked_in_by', 'status']

class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOut
        fields = ['id', 'room_booking', 'check_out_date', 'checked_out_by', 'status']

class ServiceUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceUsage
        fields = ['id', 'room_booking', 'service', 'usage_date', 'quantity', 'total_price']

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ['id', 'room_booking', 'billing_date', 'amount', 'status', 'details']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'billing', 'payment_date', 'amount', 'payment_method', 'status']

