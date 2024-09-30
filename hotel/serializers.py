from rest_framework import serializers
from .models import Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, Billing, Payment, GuestDetails
import logging
from datetime import date
from accounts.models import User

logger = logging.getLogger(__name__)

class RoomBookingSerializer(serializers.ModelSerializer):
    check_out_date = serializers.SerializerMethodField()
    checked_out_by = serializers.SerializerMethodField()
    check_in_details = serializers.SerializerMethodField()  # Added field

    class Meta:
        model = RoomBooking
        fields = ['id', 'booking', 'room', 'start_date', 'end_date', 'status', 'is_active', 'check_in_details', 'check_out_date', 'checked_out_by']

    def get_check_out_date(self, obj):
        check_out = CheckOut.objects.filter(room_booking=obj).first()
        return check_out.check_out_date if check_out else None

    def get_checked_out_by(self, obj):
        check_out = CheckOut.objects.filter(room_booking=obj).first()
        return check_out.checked_out_by.id if check_out else None

    def get_check_in_details(self, obj):
        check_in = CheckIn.objects.filter(room_booking=obj).first()
        return CheckInDetailSerializer(check_in).data if check_in else None

class RoomSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'beds', 'price', 'description', 'image', 'status', 'bookings']
        extra_kwargs = {'tenant': {'required': False}}

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
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address']

class BookingSerializer(serializers.ModelSerializer):
    rooms = RoomBookingSerializer(source='roombooking_set', many=True, read_only=True)
    guests = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_date', 'status', 'total_amount', 'tenant', 'guests', 'rooms', 'id_card']
        extra_kwargs = {
            'id_card': {'required': False, 'allow_null': True}
        }

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

class GuestDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestDetails
        fields = ['coming_from', 'going_to', 'purpose', 'guest_id', 'c_form']  # Added guest_id field

class GuestUserSerializer(serializers.ModelSerializer):
    guest_details = GuestDetailsSerializer(read_only=True)  # Include GuestDetails

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address', 'guest_details']

class CheckInSerializer(serializers.ModelSerializer):
    guests = GuestUserSerializer(many=True, read_only=True)  # Use GuestUserSerializer

    class Meta:
        model = CheckIn
        fields = ['id', 'room_booking', 'check_in_date', 'checked_in_by', 'guests']

class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOut
        fields = ['id', 'room_booking', 'check_out_date', 'checked_out_by']

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

class CheckInDetailSerializer(serializers.ModelSerializer):
    guests = GuestUserSerializer(many=True, read_only=True)

    class Meta:
        model = CheckIn
        fields = ['id', 'room_booking', 'check_in_date', 'checked_in_by', 'guests']

