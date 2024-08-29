from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.models import Table, User
from django.contrib.auth import get_user_model
from .models import Order
from .serializers import OrderSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(tenant=user.tenant)

    def create(self, request):
        user = request.user
        data = request.data
        tenant = user.tenant

        phone = data.get('phone')
        email = data.get('email')

        try:
            with transaction.atomic():
                # Check if user exists
                customer = None
                if phone:
                    customer = User.objects.filter(phone=phone).first()
                elif email:
                    customer = User.objects.filter(email=email).first()

                if customer:
                    # Update customer details if they are not empty
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')

                    if first_name:
                        customer.first_name = first_name
                    if last_name:
                        customer.last_name = last_name
                    customer.save()
                else:
                    # Create new customer
                    customer = User.objects.create_user(
                        username=email or phone,
                        email=email,
                        phone=phone,
                        first_name=data.get('first_name', ''),
                        last_name=data.get('last_name', ''),
                        password='customer',
                        role='customer'
                    )

                order_type = data.get('order_type')

                # Validate order_type and table/room requirements
                if order_type == 'dine_in':
                    table_id = data.get('table')
                    if not table_id:
                        raise ValidationError("Table is required for dine-in orders.")
                    table = get_object_or_404(Table, pk=table_id)

                    if table.occupied:
                        raise ValidationError(f"Table {table_id} is already occupied.")

                    table.occupied = True
                    table.save()
                elif order_type == 'hotel':
                    raise NotImplementedError("Hotel is not yet implemented.")
                else:
                    table = None

                # Create order
                order = Order.objects.create(
                    tenant=tenant,
                    customer=customer,
                    table=table,
                    total_price=data.get('total_price'),
                    discount=data.get('discount'),
                    coupon_used=data.get('coupon_used', []),
                    notes=data.get('notes', ''),
                    status='in_progress',
                    order_type=order_type,
                    payment_method=data.get('payment_method'),
                )
                order.food_items.set(data.get('food_items'))

                serializer = OrderSerializer(order)
                logger.info(f"Order {order.id} created by {user.username}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.exception(f"Error creating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        user = request.user
        data = request.data

        try:
            with transaction.atomic():
                order = get_object_or_404(self.get_queryset(), pk=pk)

                if order.order_type == 'dine_in' and order.table:
                    if data.get('status') in ['completed', 'cancelled']:
                        order.table.occupied = False
                        order.table.save()

                # Update order details
                order.status = data.get('status', order.status)
                order.discount = data.get('discount', order.discount)
                order.coupon_used = data.get('coupon_used', order.coupon_used)
                order.total_price = data.get('total_price', order.total_price)
                order.notes = data.get('notes', order.notes)
                order.save()

                serializer = OrderSerializer(order)
                logger.info(f"Order {order.id} updated by {user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.exception(f"Error updating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)