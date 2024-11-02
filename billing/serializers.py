from rest_framework import serializers
from .models import Bill, BillPayment
from order.serializers import OrderSerializer
from hotel.serializers import BookingSerializer

class BillSerializer(serializers.ModelSerializer):
    order_details = OrderSerializer(source='order', read_only=True)
    booking_details = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id',
            'tenant',
            'bill_number',
            'gst_bill_no',
            'bill_type',
            'order',
            'order_details',
            'booking',
            'booking_details',
            'total',
            'discount',
            'discounted_amount',
            'room_sgst',
            'room_cgst',
            'order_sgst',
            'order_cgst',
            'service_sgst',
            'service_cgst',
            'sgst_amount',
            'cgst_amount',
            'net_amount',
            'status',
            'created_at',
            'created_by',
            'modified_at',
            'modified_by'
        ]
        read_only_fields = [
            'bill_number', 
            'gst_bill_no',
            'created_at',
            'created_by',
            'modified_at',
            'modified_by'
        ]

class BillPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPayment
        fields = [
            'id',
            'bill',
            'amount',
            'payment_method',
            'payment_date',
            'payment_details',
            'created_by'
        ]
        read_only_fields = ['payment_date', 'created_by'] 