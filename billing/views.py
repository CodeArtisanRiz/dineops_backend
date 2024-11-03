from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Bill
from .serializers import BillSerializer
from .services import BillingService
from order.models import Order
from hotel.models import Booking, RoomBooking, CheckOut, CheckIn
from decimal import Decimal

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        tenant = request.user.tenant
        order_id = data.get('order_id', None)
        booking_id = data.get('booking_id', None)
        discount = Decimal(data.get('discount', '0.00'))
        bill_type = data.get('bill_type')

        # Validate bill_type
        if bill_type not in ['HOT', 'RES']:
            return Response({"error": "Invalid bill type. Must be 'HOT' or 'RES'."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that booking_id is provided if bill_type is HOT
        if bill_type == 'HOT' and not booking_id:
            return Response({"error": "Booking ID is required for HOT bill type."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that order_id is provided if bill_type is RES
        if bill_type == 'RES' and not order_id:
            return Response({"error": "Order ID is required for RES bill type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_instance = None
            if order_id:
                order_instance = Order.objects.get(id=order_id, tenant=tenant)

            total = Decimal('0.00')
            discounted_total = Decimal('0.00')
            net_total = Decimal('0.00')
            order_sgst = Decimal('0.00')
            order_cgst = Decimal('0.00')
            room_sgst = Decimal('0.00')
            room_cgst = Decimal('0.00')
            room_details = []

            if bill_type == 'RES':
                total, discounted_total, net_total, order_sgst, order_cgst = self.order_bill_calc(
                    order_instance, discount, tenant
                )

            if bill_type == 'HOT':
                total, discounted_total, net_total, order_sgst, order_cgst = self.service_bill_calc(
                    booking_id, discount, tenant
                )
                room_total, room_discounted_total, room_net_total, room_sgst, room_cgst, room_details = self.rooms_bill_calc(
                    booking_id, discount, tenant
                )
                total += room_total
                discounted_total += room_discounted_total
                net_total += room_net_total

            # Generate bill numbers
            bill_no, res_bill_no, hot_bill_no = BillingService.generate_bill_numbers(tenant, bill_type)

            # Create bill
            bill = Bill.objects.create(
                tenant=tenant,
                order_id=order_instance if bill_type == 'RES' else None,
                booking_id=Booking.objects.get(id=booking_id, tenant=tenant) if bill_type == 'HOT' else None,
                total=total,
                discount=discount,
                discounted_amount=discounted_total,
                net_amount=net_total,
                sgst_amount=order_sgst + room_sgst,
                cgst_amount=order_cgst + room_cgst,
                order_sgst=order_sgst,
                order_cgst=order_cgst,
                room_sgst=room_sgst,
                room_cgst=room_cgst,
                bill_no=bill_no,
                res_bill_no=res_bill_no if bill_type == 'RES' else None,
                hot_bill_no=hot_bill_no if bill_type == 'HOT' else None,
                bill_type=bill_type,
                created_by=request.user
            )

            # Generate GST bill number
            if bill_type == 'RES':
                bill.gst_bill_no = BillingService.generate_gst_bill_no(bill_type, bill_no, res_bill_no)
            elif bill_type == 'HOT':
                bill.gst_bill_no = BillingService.generate_gst_bill_no(bill_type, bill_no, hot_bill_no)
            
            bill.save()

            # Serialize the bill and add room details
            serializer = self.get_serializer(bill)
            response_data = serializer.data
            response_data['room_details'] = room_details  # Add room details to the response

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    def order_bill_calc(self, order_instance, discount, tenant):
        """Calculate totals, discounts, and GST amounts for a single order."""
        total = order_instance.total  # Assuming this field exists

        # Ensure discount does not exceed total
        discount = min(discount, total)

        # Calculate discounted total
        discounted_total = total - discount

        # Retrieve GST rates from tenant
        restaurant_sgst_rate = tenant.restaurant_sgst
        restaurant_cgst_rate = tenant.restaurant_cgst

        # Calculate GST amounts
        order_sgst = round(discounted_total * (restaurant_sgst_rate / 100), 2)
        order_cgst = round(discounted_total * (restaurant_cgst_rate / 100), 2)

        # Calculate net total
        net_total = discounted_total + order_sgst + order_cgst

        return total, discounted_total, net_total, order_sgst, order_cgst

    def service_bill_calc(self, booking_id, discount, tenant):
        """Calculate totals, discounts, and GST amounts for services associated with a booking."""
        total = Decimal('0.00')
        booking = Booking.objects.get(id=booking_id, tenant=tenant)

        # Fetch associated orders for the booking using the correct field
        associated_orders = Order.objects.filter(booking_id=booking.id, tenant=tenant)
        for order in associated_orders:
            total += order.total  # Add each order's total to the bill total

        # Ensure discount does not exceed total
        discount = min(discount, total)

        # Calculate discounted total
        discounted_total = total - discount

        # Retrieve GST rates from tenant
        restaurant_sgst_rate = tenant.restaurant_sgst
        restaurant_cgst_rate = tenant.restaurant_cgst

        # Calculate GST amounts
        order_sgst = round(discounted_total * (restaurant_sgst_rate / 100), 2)
        order_cgst = round(discounted_total * (restaurant_cgst_rate / 100), 2)

        # Calculate net total
        net_total = discounted_total + order_sgst + order_cgst

        return total, discounted_total, net_total, order_sgst, order_cgst

    def rooms_bill_calc(self, booking_id, discount, tenant):
        """Calculate totals, discounts, and net amounts for room charges associated with a booking."""
        booking = Booking.objects.get(id=booking_id, tenant=tenant)
        total = Decimal('0.00')
        discounted_total = Decimal('0.00')
        net_total = Decimal('0.00')
        room_sgst = Decimal('0.00')
        room_cgst = Decimal('0.00')
        room_details = []  # List to store details of each room

        # Iterate over each RoomBooking associated with the booking
        room_bookings = RoomBooking.objects.filter(booking=booking)
        for room_booking in room_bookings:
            check_out = CheckOut.objects.filter(room_booking=room_booking).first()
            check_in = CheckIn.objects.filter(room_booking=room_booking).first()

            if not check_out or not check_in:
                raise ValidationError("Room has not been checked out yet.")

            # Calculate the number of days stayed
            days_stayed = (check_out.check_out_date - check_in.check_in_date).days

            # Calculate the total for this room
            room_total = room_booking.room.price * days_stayed
            total += room_total

            # Determine GST rates based on the room price
            if room_booking.room.price > tenant.hotel_gst_limit_margin:
                room_sgst_rate = tenant.hotel_sgst_upper
                room_cgst_rate = tenant.hotel_cgst_upper
            else:
                room_sgst_rate = tenant.hotel_sgst_lower
                room_cgst_rate = tenant.hotel_cgst_lower

            # Calculate GST amounts for this room
            room_sgst_amount = round(room_total * (room_sgst_rate / 100), 2)
            room_cgst_amount = round(room_total * (room_cgst_rate / 100), 2)
            room_sgst += room_sgst_amount
            room_cgst += room_cgst_amount

            # Append room details to the list
            room_details.append({
                'room_id': room_booking.room.id,
                'room_price': room_booking.room.price,
                'days_stayed': days_stayed,
                'total': room_total,
                'cgst': room_cgst_amount,
                'sgst': room_sgst_amount
            })

        # Calculate discounted total
        discount = min(discount, total)
        discounted_total = total - discount

        # Calculate net total
        net_total = discounted_total + room_sgst + room_cgst

        return total, discounted_total, net_total, room_sgst, room_cgst, room_details
