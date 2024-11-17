from rest_framework import serializers
from .models import Bill, BillPayment

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'id',
            'tenant',
            'bill_no',
            'res_bill_no',
            'hot_bill_no',
            'gst_bill_no',
            'customer_gst',
            'bill_type',
            'order_id',
            'booking_id',
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
            'modified_by',
            'day_calculation_method',
        ]
        read_only_fields = [
            'id',
            'bill_no',
            'res_bill_no',
            'hot_bill_no',
            'gst_bill_no',
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
            'created_at',
            'created_by',
            'modified_at',
            'modified_by',
        ]

    def to_representation(self, instance):
        """Override to_representation to set non-applicable GST fields to null."""
        representation = super().to_representation(instance)
        
        # Set non-applicable GST fields to null for RES type
        if instance.bill_type == 'RES':
            representation['room_sgst'] = None
            representation['room_cgst'] = None
            representation['service_sgst'] = None
            representation['service_cgst'] = None
        # For HOT type, all GST fields are applicable, so no need to set any to null

        return representation

class BillPaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=['paid', 'partial'], write_only=True)

    class Meta:
        model = BillPayment
        fields = [
            'id',
            'bill_id',
            'paid_amount',
            'payment_method',
            'payment_date',
            'payment_details',
            'created_by',
            'status',  # Extra field for payment status
        ]
        read_only_fields = ['id', 'payment_date', 'created_by']

    def validate(self, data):
        bill = data['bill_id']
        if bill.status == 'paid':
            raise serializers.ValidationError("No new payments can be made as the bill is already fully paid.")
        return data

    def create(self, validated_data):
        status = validated_data.pop('status', 'partial')
        bill = validated_data['bill_id']
        validated_data['bill_amount'] = bill.net_amount  # Fetch bill_amount from Bill's net_amount
        bill_payment = super().create(validated_data)
        bill_payment.update_bill_status(status)
        return bill_payment
