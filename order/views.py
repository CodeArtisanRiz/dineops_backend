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
from foods.models import FoodItem
from billing.models import Bill
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()
logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    
    def get_queryset(self):
        # Use select_related and prefetch_related to optimize query performance
        if getattr(self, 'swagger_fake_view', False):
            # Return an empty queryset for schema generation
            return Order.objects.none()
        return Order.objects.filter(tenant=self.request.user.tenant).select_related('customer', 'room_id', 'booking_id').prefetch_related('food_items', 'tables')

    @swagger_auto_schema(tags=['Orders'])
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
                    city=data.get('city', ''),
                    state=data.get('state', ''),
                    country=data.get('country', ''),
                    pin=data.get('pin', ''),
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

                # Sort food_items and quantities
                food_items = data.get('food_items', [])
                quantities = data.get('quantity', [])
                sorted_pairs = sorted(zip(food_items, quantities), key=lambda x: x[0])
                sorted_food_items, sorted_quantities = zip(*sorted_pairs) if sorted_pairs else ([], [])

                # Create order
                order = Order(
                    tenant=tenant,
                    customer=customer,
                    notes=data.get('notes', ''),
                    status='in_progress',
                    order_type=order_type,
                    quantity=list(sorted_quantities),
                    room_id=room if order_type == 'hotel' else None,
                    booking_id=booking if order_type == 'hotel' else None
                )

                # Save the order to generate an ID
                order.save()

                # Set many-to-many relationships
                order.food_items.set(sorted_food_items)
                order.tables.set(tables)
                order.kot_count = data.get('kot_count', 0)

                # Calculate totals
                total = Decimal('0.00')
                for food_item, qty in zip(order.food_items.all(), order.quantity):
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

    @swagger_auto_schema(tags=['Orders'])
    def update(self, request, pk=None, partial=False):
        try:
            with transaction.atomic():
                logger.info(f"Starting update for order ID: {pk}")
                order = get_object_or_404(self.get_queryset(), pk=pk)
                
                # Log the current order status
                logger.debug(f"Current order status: {order.status}")

                # Prevent updates if the order status is 'served'
                if order.status == 'served':
                    return Response({"error": "Order already served and cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)
                
                data = request.data
                logger.debug(f"Request data: {data}")

                # Check if the order is associated with any bills
                associated_bills = Bill.objects.filter(order_id=order.id)
                if associated_bills.exists():
                    logger.info(f"Found {associated_bills.count()} associated bills for order ID: {pk}")
                    
                    # Log the current status of the bills before updating
                    for bill in associated_bills:
                        logger.debug(f"Current status of bill ID {bill.id}: {bill.status}")
                    
                    # Update the status of associated bills to 'cancelled'
                    updated_count = associated_bills.update(status='cancelled')
                    
                    # Log the updated status of the bills
                    for bill in associated_bills:
                        logger.debug(f"Updated status of bill ID {bill.id}: {bill.status}")
                    
                    logger.info(f"Updated status of {updated_count} bills to 'cancelled' for order ID: {pk}")
                else:
                    logger.info(f"No associated bills found for order ID: {pk}")

                # Capture the original status before updating
                original_status = order.status
                logger.debug(f"Original order status: {original_status}")

                # Update customer details if provided
                if 'phone' in data or 'email' in data:
                    logger.info("Updating customer details")
                    customer_id = get_or_create_user(
                        username=data.get('phone', order.customer.phone) or data.get('email', order.customer.email),
                        email=data.get('email', order.customer.email),
                        first_name=data.get('first_name', order.customer.first_name),
                        last_name=data.get('last_name', order.customer.last_name),
                        role='customer',
                        phone=data.get('phone', order.customer.phone),
                        address_line_1=data.get('address_line_1', ''),
                        address_line_2=data.get('address_line_2', ''),
                        city=data.get('city', ''),
                        state=data.get('state', ''),
                        country=data.get('country', ''),
                        pin=data.get('pin', ''),

                        password=None,
                        tenant=request.user.tenant
                    )
                    order.customer = User.objects.get(id=customer_id)
                    logger.debug(f"Updated customer ID: {customer_id}")

                # Handle table updates if 'tables' is in the request data
                if 'tables' in data:
                    logger.info("Updating tables")
                    table_ids = data.get('tables', [])
                    if not table_ids:
                        logger.warning("No tables provided for dine-in order")
                        return Response({"error": "At least one table is required for dine-in orders."}, status=status.HTTP_400_BAD_REQUEST)

                    # Free previously occupied tables
                    for previous_table in order.tables.all():
                        previous_table.occupied = False
                        previous_table.order = None
                        previous_table.save()
                        logger.debug(f"Freed table ID: {previous_table.id}")

                    # Assign new tables
                    tables = []
                    for table_id in table_ids:
                        table = get_object_or_404(Table, pk=table_id)
                        if table.occupied:
                            logger.warning(f"Table {table_id} is already occupied")
                            return Response({"error": f"Table {table_id} is already occupied."}, status=status.HTTP_400_BAD_REQUEST)
                        table.occupied = True
                        table.order = order.id
                        table.save()
                        tables.append(table)
                        logger.debug(f"Assigned table ID: {table_id}")
                    
                    # Clear previous tables and set new ones
                    order.tables.set(tables)
                    logger.debug(f"Updated tables: {table_ids}")

                # Handle food_items updates if 'food_items' is in the request data
                if 'food_items' in data:
                    logger.info("Updating food items")
                    food_item_ids = data.get('food_items', [])
                    if not food_item_ids:
                        logger.warning("No food items provided")
                        return Response({"error": "At least one food item is required."}, status=status.HTTP_400_BAD_REQUEST)

                    # Check if all food items exist
                    existing_food_items = FoodItem.objects.filter(id__in=food_item_ids)
                    existing_ids = set(existing_food_items.values_list('id', flat=True))
                    missing_ids = set(food_item_ids) - existing_ids

                    if missing_ids:
                        logger.error(f"Food items not found: {missing_ids}")
                        return Response({"error": f"Food items with IDs {missing_ids} not found."}, status=status.HTTP_400_BAD_REQUEST)

                    # Sort food_items and quantities
                    quantities = data.get('quantity', [])
                    sorted_pairs = sorted(zip(food_item_ids, quantities), key=lambda x: x[0])
                    sorted_food_items, sorted_quantities = zip(*sorted_pairs) if sorted_pairs else ([], [])

                    # Clear previous food items and set new ones
                    order.food_items.set(sorted_food_items)
                    order.quantity = list(sorted_quantities)
                    logger.debug(f"Updated food items: {sorted_food_items}")

                # Update quantity if provided
                if 'quantity' in data and not 'food_items' in data:
                    quantity = data.get('quantity', [])
                    if len(quantity) != len(order.food_items.all()):
                        logger.warning("Mismatch between number of food_items[] and quantity[]")
                        return Response({"error": "The number of items in food_items[] and quantity[] must match."}, status=status.HTTP_400_BAD_REQUEST)
                    order.quantity = quantity
                    logger.debug(f"Updated quantity: {quantity}")

                # Update other order fields
                for attr, value in data.items():
                    if hasattr(order, attr) and attr not in ['tables', 'food_items', 'quantity']:
                        setattr(order, attr, value)
                        logger.debug(f"Updated {attr} to {value}")

                # Special handling for 'kot' status
                if data.get('status') == 'kot':
                    order.kot_count += 1
                    logger.debug(f"Incremented KOT count to {order.kot_count}")

                # Free tables if the status changes to 'billed', 'settled', or 'cancelled'
                if order.status in ['billed', 'settled', 'cancelled'] and original_status != order.status:
                    for table in order.tables.all():
                        table.occupied = False
                        table.order = None
                        table.save()
                        logger.debug(f"Freed table ID: {table.id} due to status change")

                # Update modified_at and modified_by
                order.modified_at.append(timezone.now().isoformat())
                order.modified_by.append(request.user.id)
                logger.debug(f"Updated modified_at and modified_by")

                # Calculate totals and save
                total = Decimal('0.00')
                for food_item, qty in zip(order.food_items.all(), order.quantity):
                    item_price = Decimal(str(food_item.price))
                    item_qty = Decimal(str(qty))
                    total += item_price * item_qty

                order.total = total
                order.save()
                logger.info(f"Order ID {pk} updated successfully")

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error updating order ID {pk}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)