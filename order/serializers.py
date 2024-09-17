from rest_framework import serializers
from .models import Order, FoodItem

class OrderSerializer(serializers.ModelSerializer):
    food_items = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodItem.objects.all())
    quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=1), 
        required=True
    )
    phone = serializers.SerializerMethodField()
    table_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['modified_at', 'modified_by']  # Make these fields read-only

    def get_phone(self, obj):
        return obj.customer.phone

    def get_table_number(self, obj):
        return obj.table.id if obj.table else None

    def validate(self, data):
        if len(data['food_items']) != len(data['quantity']):
            raise serializers.ValidationError("The number of items and quantities must match.")
        return data

    def create(self, validated_data):
        food_items = validated_data.pop('food_items')
        quantity = validated_data.pop('quantity')

        order = Order.objects.create(**validated_data)
        order.food_items.set(food_items)
        order.quantity = quantity  # Ensure quantity is set
        order.save()

        return order

    def update(self, instance, validated_data):
        food_items = validated_data.pop('food_items', None)
        quantity = validated_data.pop('quantity', None)

        if food_items is not None:
            instance.food_items.set(food_items)
        if quantity is not None:
            instance.quantity = quantity  # Ensure quantity is updated

        instance.status = validated_data.get('status', instance.status)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.coupon_used = validated_data.get('coupon_used', instance.coupon_used)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()

        return instance