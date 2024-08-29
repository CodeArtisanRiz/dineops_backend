from rest_framework import serializers
from .models import Order, FoodItem

# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    food_items = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodItem.objects.all())
    quantity = serializers.ListField(
        child=serializers.IntegerField(min_value=1), 
        write_only=True, 
        required=True
    )

    class Meta:
        model = Order
        # fields = [
        #     'tenant', 'customer', 'order_type', 'table', 'payment_method',
        #     'total_price', 'discount', 'coupon_used', 'notes', 'food_items', 
        #     'quantity', 'status'
        # ]
        fields = '__all__'

    def validate(self, data):
        if len(data['food_items']) != len(data['quantity']):
            raise serializers.ValidationError("The number of items and quantities must match.")
        return data

    def create(self, validated_data):
        food_items = validated_data.pop('food_items')
        quantity = validated_data.pop('quantity')

        order = Order.objects.create(**validated_data)
        order.food_items.set(food_items)
        order.quantity = quantity
        order.save()

        return order

    def update(self, instance, validated_data):
        food_items = validated_data.pop('food_items', None)
        quantity = validated_data.pop('quantity', None)

        if food_items is not None:
            instance.food_items.set(food_items)
        if quantity is not None:
            instance.quantity = quantity

        instance.status = validated_data.get('status', instance.status)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.coupon_used = validated_data.get('coupon_used', instance.coupon_used)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()

        return instance