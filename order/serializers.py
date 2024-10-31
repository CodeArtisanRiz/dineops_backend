from rest_framework import serializers
from .models import Order, FoodItem, Table
from hotel.models import Room, Booking  # Import Room and Booking models

class OrderSerializer(serializers.ModelSerializer):
    food_items = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodItem.objects.all())
    quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=1), 
        required=True
    )
    phone = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()  # Add this line
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), required=False, allow_null=True)  # New field
    booking_id = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=False, allow_null=True)  # Updated field

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at', 'modified_by']

    def get_phone(self, obj):
        return obj.customer.phone

    def get_table_numbers(self, obj):  # Update to handle multiple tables
        return [table.id for table in obj.tables.all()]

    def get_customer(self, obj):  # Add this method
        return {
            "id": obj.customer.id,
            "username": obj.customer.username,
            "email": obj.customer.email,
            "first_name": obj.customer.first_name,
            "last_name": obj.customer.last_name,
            "phone": obj.customer.phone,
            "address_line_1": obj.customer.address_line_1,
            "address_line_2": obj.customer.address_line_2,
        }

    def validate(self, data):
        order_type = data.get('order_type')
        
        if order_type == 'dine_in':
            if not data.get('tables'):
                raise serializers.ValidationError("At least one table is required for dine-in orders.")
            if data.get('room_id') or data.get('booking_id'):
                raise serializers.ValidationError("Room and booking should be null for dine-in orders.")
        
        elif order_type == 'hotel':
            if not data.get('room_id') or not data.get('booking_id'):
                raise serializers.ValidationError("Room ID and Booking ID are required for hotel orders.")
            if data.get('tables'):
                raise serializers.ValidationError("Tables should be null for hotel orders.")
        
        elif order_type in ['take_away', 'delivery', 'online']:
            if data.get('tables'):
                raise serializers.ValidationError("Tables should be null for take-away/delivery/online orders.")
            # if data.get('room_id') or data.get('booking_id'):
            #     raise serializers.ValidationError("Room and booking should be null for take-away/delivery/online orders.")
        
        else:
            raise serializers.ValidationError("Invalid order type. Valid types are: hotel, dine_in, take_away, delivery, online")

        if len(data['food_items']) != len(data['quantity']):
            raise serializers.ValidationError("The number of items and quantities must match.")
        
        if all(data.get(field) is not None for field in ['sub_total', 'total_amount', 'net_amount']):
            if data['sub_total'] < 0 or data['total_amount'] < 0 or data['net_amount'] < 0:
                raise serializers.ValidationError("Price fields cannot be negative.")
            
            if data['net_amount'] > data['total_amount']:
                raise serializers.ValidationError("Net amount cannot be greater than total amount.")
        
        return data

    def create(self, validated_data):
        food_items = validated_data.pop('food_items')
        quantity = validated_data.pop('quantity')
        tables = validated_data.pop('tables', [])  # Ensure tables is handled

        order = Order.objects.create(**validated_data)
        order.food_items.set(food_items)
        order.quantity = quantity  # Ensure quantity is set
        order.tables.set(tables)  # Set the list of tables
        order.kot_count = validated_data.get('kot_count', 0)  # Ensure kot_count is set
        order.save()

        return order

    def update(self, instance, validated_data):
        food_items = validated_data.pop('food_items', None)
        quantity = validated_data.pop('quantity', None)
        tables = validated_data.pop('tables', None)  # Ensure tables is handled

        if food_items is not None:
            instance.food_items.set(food_items)
        if quantity is not None:
            instance.quantity = quantity  # Ensure quantity is updated
        if tables is not None:
            instance.tables.set(tables)  # Set the list of tables

        instance.status = validated_data.get('status', instance.status)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.coupon_used = validated_data.get('coupon_used', instance.coupon_used)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.kot_count = validated_data.get('kot_count', instance.kot_count)  # Ensure kot_count is updated
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)  # Ensure payment_method is updated
        instance.save()

        return instance