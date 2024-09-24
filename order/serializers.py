from rest_framework import serializers
from .models import Order, FoodItem, Table

class OrderSerializer(serializers.ModelSerializer):
    food_items = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodItem.objects.all())
    quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=1), 
        required=True
    )
    phone = serializers.SerializerMethodField()
    # table_numbers = serializers.SerializerMethodField()  # Update to handle multiple tables
    customer = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['modified_at', 'modified_by']

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
            "address": obj.customer.address,
        }

    def validate(self, data):
        if len(data['food_items']) != len(data['quantity']):
            raise serializers.ValidationError("The number of items and quantities must match.")
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