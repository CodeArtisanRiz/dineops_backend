from rest_framework import serializers
from .models import Bill

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
            'modified_by'
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
            'modified_by'
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
