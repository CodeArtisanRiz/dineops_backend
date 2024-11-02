from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.models import User
from foods.models import Table
from django.contrib.auth import get_user_model
from .models import Order
from .serializers import OrderSerializer
import logging
from utils.get_or_create_user import get_or_create_user
from hotel.models import Room, Booking, RoomBooking, CheckIn, CheckOut
from decimal import Decimal
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(tenant=self.request.user.tenant)

    def create(self, request):
        try:
            with transaction.atomic():
                user = request.user
                data = request.data
                tenant = user.tenant

                # Get or create the customer
                customer_id = get_or_create_user(
                    username=data.get('phone') or data.get('email'),
                    email=data.get('email'),
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    role='customer',
                    phone=data.get('phone'),
                    address_line_1=data.get('address_line_1', ''),
                    address_line_2=data.get('address_line_2', ''),
                    password='customer',
                    tenant=tenant
                )
                customer = User.objects.get(id=customer_id)

                order_type = data.get('order_type')
                room, booking, tables = None, None, []

                if order_type == 'hotel':
                    room = get_object_or_404(Room, pk=data.get('room_id'))
                    booking = get_object_or_404(Booking, pk=data.get('booking_id'))
                    room_booking = get_object_or_404(RoomBooking, room=room, booking=booking)
                    if not CheckIn.objects.filter(room_booking=room_booking).exists():
                        return Response({"error": "Guest not checked in yet."}, status=status.HTTP_400_BAD_REQUEST)
                    if CheckOut.objects.filter(room_booking=room_booking).exists():
                        return Response({"error": "Guest already checked out."}, status=status.HTTP_400_BAD_REQUEST)

                elif order_type == 'dine_in':
                    table_ids = data.get('tables', [])
                    if not table_ids:
                        return Response({"error": "At least one table is required for dine-in orders."}, status=status.HTTP_400_BAD_REQUEST)
                    for table_id in table_ids:
                        table = get_object_or_404(Table, pk=table_id)
                        if table.occupied:
                            return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                        table.occupied = True
                        table.save()
                        tables.append(table)

                elif order_type not in ['take_away', 'delivery', 'online']:
                    return Response({"error": "Invalid order type."}, status=status.HTTP_400_BAD_REQUEST)

                # Create order
                order = Order(
                    tenant=tenant,
                    customer=customer,
                    notes=data.get('notes', ''),
                    status='in_progress',
                    order_type=order_type,
                    quantity=data.get('quantity', []),
                    room_id=room,
                    booking_id=booking
                )

                # Save the order to generate an ID
                order.save()

                # Set many-to-many relationships
                order.food_items.set(data.get('food_items'))
                order.tables.set(tables)
                order.kot_count = data.get('kot_count', 0)

                # Calculate totals
                total = Decimal('0.00')
                food_items = order.food_items.all()
                quantities = order.quantity

                if food_items and quantities and len(food_items) == len(quantities):
                    for food_item, qty in zip(food_items, quantities):
                        item_price = Decimal(str(food_item.price))
                        item_qty = Decimal(str(qty))
                        total += item_price * item_qty

                order.total = total
                order.save()

                # Update tables with the order ID
                for table in tables:
                    table.order = order.id
                    table.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(f"Error creating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, partial=False):
        try:
            with transaction.atomic():
                order = get_object_or_404(self.get_queryset(), pk=pk)
                data = request.data

                # Capture the original status before updating
                original_status = order.status

                # Update customer details
                customer_id = get_or_create_user(
                    username=data.get('phone', order.customer.phone) or data.get('email', order.customer.email),
                    email=data.get('email', order.customer.email),
                    first_name=data.get('first_name', order.customer.first_name),
                    last_name=data.get('last_name', order.customer.last_name),
                    role='customer',
                    phone=data.get('phone', order.customer.phone),
                    address_line_1=data.get('address_line_1', ''),
                    address_line_2=data.get('address_line_2', ''),
                    password=None,
                    tenant=request.user.tenant
                )
                order.customer = User.objects.get(id=customer_id)

                # Handle table updates if 'tables' is in the request data
                if 'tables' in data:
                    table_ids = data.get('tables', [])
                    if not table_ids:
                        return Response({"error": "At least one table is required for dine-in orders."}, status=status.HTTP_400_BAD_REQUEST)

                    # Free previously occupied tables
                    for previous_table in order.tables.all():
                        previous_table.occupied = False
                        previous_table.order = None
                        previous_table.save()

                    # Assign new tables
                    tables = []
                    for table_id in table_ids:
                        table = get_object_or_404(Table, pk=table_id)
                        if table.occupied:
                            return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                        table.occupied = True
                        table.order = order.id
                        table.save()
                        tables.append(table)
                    order.tables.set(tables)  # Use set() to update the many-to-many relationship

                # Update order fields
                for attr, value in data.items():
                    if hasattr(order, attr):
                        setattr(order, attr, value)

                # Special handling for 'kot' status
                if data.get('status') == 'kot':
                    order.kot_count += 1

                # Free tables if the status changes to 'billed', 'settled', or 'cancelled'
                if order.status in ['billed', 'settled', 'cancelled'] and original_status != order.status:
                    for table in order.tables.all():
                        table.occupied = False
                        table.order = None
                        table.save()

                # Update modified_at and modified_by
                order.modified_at.append(timezone.now().isoformat())
                order.modified_by.append(request.user.id)

                # Calculate totals and save
                order.calculate_totals()
                order.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error updating order: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)