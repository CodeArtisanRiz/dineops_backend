from rest_framework import serializers
from .models import Order, FoodItem, Table
from hotel.models import Room, Booking
from decimal import Decimal

class OrderSerializer(serializers.ModelSerializer):
    food_items = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodItem.objects.all())
    quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=1), 
        required=True
    )
    phone = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), required=False, allow_null=True)
    booking_id = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'tenant', 'customer', 'created_at', 'modified_at', 'modified_by',
            'status', 'order_type', 'tables', 'room_id', 'booking_id',
            'food_items', 'quantity', 'notes', 'kot_count',
            'total',
            'phone', 'customer'
        ]
        read_only_fields = ['created_at', 'modified_at', 'modified_by', 'total']

    def get_phone(self, obj):
        return obj.customer.phone

    def get_table_numbers(self, obj):
        return [table.id for table in obj.tables.all()]

    def get_customer(self, obj):
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
        
        else:
            raise serializers.ValidationError("Invalid order type. Valid types are: hotel, dine_in, take_away, delivery, online")

        if len(data['food_items']) != len(data['quantity']):
            raise serializers.ValidationError("The number of items and quantities must match.")
        
        return data

    def create(self, validated_data):
        food_items = validated_data.pop('food_items')
        quantity = validated_data.pop('quantity')
        tables = validated_data.pop('tables', [])
        discount = validated_data.get('discount', Decimal('0.00'))

        # Create order
        order = Order.objects.create(
            **validated_data,
            discount=discount
        )
        
        # Set related fields
        order.food_items.set(food_items)
        order.quantity = quantity
        order.tables.set(tables)
        
        # Calculate totals and save
        order.calculate_totals()
        order.save()

        return order

    def update(self, instance, validated_data):
        food_items = validated_data.pop('food_items', None)
        quantity = validated_data.pop('quantity', None)
        tables = validated_data.pop('tables', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update related fields if provided
        if food_items is not None:
            instance.food_items.set(food_items)
        if quantity is not None:
            instance.quantity = quantity
        if tables is not None:
            instance.tables.set(tables)

        # Calculate totals and save
        instance.calculate_totals()
        instance.save()

        return instance