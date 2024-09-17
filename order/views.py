from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.models import User
from foods.models import Table
from django.contrib.auth import get_user_model
from .models import Order
from .serializers import OrderSerializer
import logging
from utils.get_or_create_user import get_or_create_user
from django.utils import timezone

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
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        address_line_1 = data.get('address_line_1', '')
        address_line_2 = data.get('address_line_2', '')
        dob = data.get('dob', None)
        address = f"{address_line_1} {address_line_2}".strip()

        try:
            with transaction.atomic():
                # Use get_or_create_user to get or create the customer
                customer_id = get_or_create_user(
                    username= phone or email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='customer',
                    phone=phone,
                    address=address,
                    password='customer',
                    tenant=tenant
                )
                customer = User.objects.get(id=customer_id)

                order_type = data.get('order_type')

                # Validate order_type and table/room requirements
                if order_type == 'dine_in':
                    table_id = data.get('table')
                    if not table_id:
                        return Response({"error": "Table is required for dine-in orders."}, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        table = Table.objects.get(pk=table_id)
                    except Table.DoesNotExist:
                        return Response({"error": f"Table {table_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                    if table.occupied:
                        return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)

                    table.occupied = True
                    table.save()
                elif order_type == 'hotel':
                    return Response({"error": "Hotel is not yet implemented."}, status=status.HTTP_400_BAD_REQUEST)
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
                    quantity=data.get('quantity', [])  # Ensure quantity is set
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
                order.quantity = data.get('quantity', order.quantity)  # Ensure quantity is updated
                
                # Update modified_at and modified_by
                order.modified_at.append(str(timezone.now()))
                order.modified_by.append(f"{user.username}({user.id})")
                
                order.save()

                serializer = OrderSerializer(order)
                logger.info(f"Order {order.id} updated by {user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.exception(f"Error updating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Table.DoesNotExist:
            logger.exception("Table does not exist.")
            return Response({"error": "Table does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk=None):
        user = request.user
        data = request.data

        try:
            with transaction.atomic():
                order = get_object_or_404(self.get_queryset(), pk=pk)

                if order.order_type == 'dine_in' and order.table:
                    if data.get('status') in ['completed', 'cancelled']:
                        order.table.occupied = False
                        order.table.save()

                # Update order details partially
                if 'status' in data:
                    order.status = data['status']
                if 'discount' in data:
                    order.discount = data['discount']
                if 'coupon_used' in data:
                    order.coupon_used = data['coupon_used']
                if 'total_price' in data:
                    order.total_price = data['total_price']
                if 'notes' in data:
                    order.notes = data['notes']
                if 'quantity' in data:
                    order.quantity = data['quantity']  # Ensure quantity is updated
                
                # Update modified_at and modified_by
                order.modified_at.append(str(timezone.now()))
                order.modified_by.append(f"{user.username}({user.id})")
                
                order.save()

                serializer = OrderSerializer(order)
                logger.info(f"Order {order.id} partially updated by {user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.exception(f"Error partially updating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Table.DoesNotExist:
            logger.exception("Table does not exist.")
            return Response({"error": "Table does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)