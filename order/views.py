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
                    table_ids = data.get('tables', [])  # Change 'table' to 'tables'
                    if not table_ids:
                        return Response({"error": "At least one table is required for dine-in orders."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    tables = []
                    for table_id in table_ids:
                        try:
                            table = Table.objects.get(pk=table_id)
                            if table.occupied:
                                return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                            table.occupied = True
                            table.save()
                            tables.append(table)
                        except Table.DoesNotExist:
                            return Response({"error": f"Table {table_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                elif order_type == 'hotel':
                    return Response({"error": "Hotel is not yet implemented."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    tables = []

                # Create order
                order = Order.objects.create(
                    tenant=tenant,
                    customer=customer,
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
                order.tables.set(tables)  # Set the list of tables
                order.kot_count = data.get('kot_count', 0)  # Ensure kot_count is set

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

                # Update user details if provided
                phone = data.get('phone', order.customer.phone)
                email = data.get('email', order.customer.email)
                first_name = data.get('first_name', order.customer.first_name)
                last_name = data.get('last_name', order.customer.last_name)
                address_line_1 = data.get('address_line_1', '')
                address_line_2 = data.get('address_line_2', '')
                address = f"{address_line_1} {address_line_2}".strip()
                dob = data.get('dob', order.customer.dob)

                customer_id = get_or_create_user(
                    username=phone or email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='customer',
                    phone=phone,
                    address=address,
                    password=None,  # No need to update password
                    tenant=user.tenant
                )
                order.customer = User.objects.get(id=customer_id)

                if data.get('status') in ['completed', 'cancelled']:
                    for table in order.tables.all():
                        table.occupied = False
                        table.save()
                # Free the previous tables if the tables are being updated
                elif order.tables.exists() and 'tables' in data:
                    for previous_table in order.tables.all():
                        previous_table.occupied = False
                        previous_table.save()

                    # Update tables if provided
                    if 'tables' in data:
                        table_ids = data['tables']
                        tables = []
                        for table_id in table_ids:
                            table = Table.objects.get(pk=table_id)
                            if table.occupied:
                                return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                            table.occupied = True
                            table.save()
                            tables.append(table)
                        order.tables.set(tables)
                    else:
                        order.tables.clear()

                # Update order details
                if data.get('status') == 'kot':
                    order.kot_count += 1  # Increment kot_count if status is 'kot'
                
                order.status = data.get('status', order.status)
                order.discount = data.get('discount', order.discount)
                order.coupon_used = data.get('coupon_used', order.coupon_used)
                order.total_price = data.get('total_price', order.total_price)
                order.notes = data.get('notes', order.notes)
                order.quantity = data.get('quantity', order.quantity)  # Ensure quantity is updated
                order.kot_count = data.get('kot_count', order.kot_count)  # Ensure kot_count is updated
                order.payment_method = data.get('payment_method', order.payment_method)  # Ensure payment_method is updated

                # Update food_items if provided
                if 'food_items' in data:
                    order.food_items.set(data['food_items'])

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

    def partial_update(self, request, pk=None):
        user = request.user
        data = request.data

        try:
            with transaction.atomic():
                order = get_object_or_404(self.get_queryset(), pk=pk)

                # Update user details if provided
                phone = data.get('phone', order.customer.phone)
                email = data.get('email', order.customer.email)
                first_name = data.get('first_name', order.customer.first_name)
                last_name = data.get('last_name', order.customer.last_name)
                address_line_1 = data.get('address_line_1', '')
                address_line_2 = data.get('address_line_2', '')
                address = f"{address_line_1} {address_line_2}".strip()
                dob = data.get('dob', order.customer.dob)

                customer_id = get_or_create_user(
                    username=phone or email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='customer',
                    phone=phone,
                    address=address,
                    password=None,  # No need to update password
                    tenant=user.tenant
                )
                order.customer = User.objects.get(id=customer_id)

                if data.get('status') in ['completed', 'cancelled']:
                    for table in order.tables.all():
                        table.occupied = False
                        table.save()

                # Free the previous tables if the tables are being updated
                elif order.tables.exists() and 'tables' in data:
                    for previous_table in order.tables.all():
                        previous_table.occupied = False
                        previous_table.save()

                    # Update tables if provided
                    if 'tables' in data:
                        table_ids = data['tables']
                        tables = []
                        for table_id in table_ids:
                            table = Table.objects.get(pk=table_id)
                            if table.occupied:
                                return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                            table.occupied = True
                            table.save()
                            tables.append(table)
                        order.tables.set(tables)
                    else:
                        order.tables.clear()

                # Update order details partially
                if data.get('status') == 'kot':
                    order.kot_count += 1  # Increment kot_count if status is 'kot'
                
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
                # if 'kot_count' in data:
                #     order.kot_count = data['kot_count']  # Ensure kot_count is updated
                if 'payment_method' in data:
                    order.payment_method = data['payment_method']  # Ensure payment_method is updated

                # Update food_items if provided
                if 'food_items' in data:
                    order.food_items.set(data['food_items'])

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