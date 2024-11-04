from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Bill
from .serializers import BillSerializer
from .services import BillingService
from order.models import Order
from hotel.models import Booking, RoomBooking, CheckOut, CheckIn
from decimal import Decimal
from hotel.models import ServiceUsage
import logging

logger = logging.getLogger(__name__)

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        tenant = request.user.tenant
        order_id = data.get('order_id', None)
        booking_id = data.get('booking_id', None)
        room_discount = Decimal(data.get('room_discount', '0.00'))
        order_discount = Decimal(data.get('order_discount', '0.00'))
        service_discount = Decimal(data.get('service_discount', '0.00'))
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
            total = Decimal('0.00')
            discounted_total = Decimal('0.00')
            net_total = Decimal('0.00')
            order_sgst = Decimal('0.00')
            order_cgst = Decimal('0.00')
            room_sgst = Decimal('0.00')
            room_cgst = Decimal('0.00')
            service_sgst = Decimal('0.00')
            service_cgst = Decimal('0.00')
            room_details = []
            service_details = []
            order_details = []

            if bill_type == 'HOT':
                # Calculate room totals
                room_bookings = RoomBooking.objects.filter(booking_id=booking_id)
                room_total = Decimal('0.00')
                for room_booking in room_bookings:
                    check_out = CheckOut.objects.filter(room_booking=room_booking).first()
                    check_in = CheckIn.objects.filter(room_booking=room_booking).first()
                    days_stayed = (check_out.check_out_date - check_in.check_in_date).days
                    room_price_total = room_booking.room.price * days_stayed
                    room_total += room_price_total
                    room_sgst_amount = round(room_price_total * (tenant.hotel_sgst_lower / 100), 2)
                    room_cgst_amount = round(room_price_total * (tenant.hotel_cgst_lower / 100), 2)
                    room_details.append({
                        'room_id': room_booking.room.id,
                        'room_price': room_booking.room.price,
                        'days_stayed': days_stayed,
                        'total': room_price_total,
                        'cgst': room_cgst_amount,
                        'sgst': room_sgst_amount
                    })
                    logger.info(f"Room {room_booking.room.id}: Price {room_booking.room.price}, Days {days_stayed}, Total {room_price_total}, SGST {room_sgst_amount}, CGST {room_cgst_amount}")

                room_discounted_total = room_total - min(room_discount, room_total)
                room_sgst = round(room_discounted_total * (tenant.hotel_sgst_lower / 100), 2)
                room_cgst = round(room_discounted_total * (tenant.hotel_cgst_lower / 100), 2)
                room_net_total = room_discounted_total + room_sgst + room_cgst

                # Calculate service totals
                service_usages = ServiceUsage.objects.filter(booking_id=booking_id)
                service_total = Decimal('0.00')
                for service_usage in service_usages:
                    service_price = service_usage.service_id.price
                    service_total += service_price
                    service_sgst_amount = round(service_price * (tenant.service_sgst_lower / 100), 2)
                    service_cgst_amount = round(service_price * (tenant.service_cgst_lower / 100), 2)
                    service_details.append({
                        'room_id': service_usage.room_id.id,
                        'service_id': service_usage.service_id.id,
                        'service_name': service_usage.service_id.name,
                        'price': service_price,
                        'cgst': service_cgst_amount,
                        'sgst': service_sgst_amount
                    })
                    logger.info(f"Service {service_usage.service_id.id}: Name {service_usage.service_id.name}, Price {service_price}, SGST {service_sgst_amount}, CGST {service_cgst_amount}")

                service_discounted_total = service_total - min(service_discount, service_total)
                service_sgst = round(service_discounted_total * (tenant.service_sgst_lower / 100), 2)
                service_cgst = round(service_discounted_total * (tenant.service_cgst_lower / 100), 2)
                service_net_total = service_discounted_total + service_sgst + service_cgst

                # Calculate order totals
                orders = Order.objects.filter(booking_id=booking_id, tenant=tenant)
                order_total = Decimal('0.00')
                for order in orders:
                    order_total += order.total
                    order_sgst_amount = round(order.total * (tenant.restaurant_sgst / 100), 2)
                    order_cgst_amount = round(order.total * (tenant.restaurant_cgst / 100), 2)
                    order_details.append({
                        'order_id': order.id,
                        'total': order.total,
                        'cgst': order_cgst_amount,
                        'sgst': order_sgst_amount
                    })
                    logger.info(f"Order {order.id}: Total {order.total}, SGST {order_sgst_amount}, CGST {order_cgst_amount}")

                order_discounted_total = order_total - min(order_discount, order_total)
                order_sgst = round(order_discounted_total * (tenant.restaurant_sgst / 100), 2)
                order_cgst = round(order_discounted_total * (tenant.restaurant_cgst / 100), 2)
                order_net_total = order_discounted_total + order_sgst + order_cgst

                # Sum up all totals
                total += room_total + service_total + order_total
                discounted_total += room_discounted_total + service_discounted_total + order_discounted_total
                net_total += room_net_total + service_net_total + order_net_total

                # Log the detailed breakdown
                logger.info(f"Bill Calculation Summary:\n"
                            f"Rooms Total: {room_total}, Discounted: {room_discounted_total}, SGST: {room_sgst}, CGST: {room_cgst}\n"
                            f"Services Total: {service_total}, Discounted: {service_discounted_total}, SGST: {service_sgst}, CGST: {service_cgst}\n"
                            f"Orders Total: {order_total}, Discounted: {order_discounted_total}, SGST: {order_sgst}, CGST: {order_cgst}\n"
                            f"Overall Total: {total}, Discounted Total: {discounted_total}, Net Total: {net_total}")

            elif bill_type == 'RES':
                # Calculate order totals for RES
                try:
                    order = Order.objects.get(id=order_id, tenant=tenant)
                    order_total = order.total
                    order_discounted_total = order_total - min(order_discount, order_total)
                    order_sgst = round(order_discounted_total * (tenant.restaurant_sgst / 100), 2)
                    order_cgst = round(order_discounted_total * (tenant.restaurant_cgst / 100), 2)
                    order_net_total = order_discounted_total + order_sgst + order_cgst

                    order_details.append({
                        'order_id': order.id,
                        'total': order.total,
                        'cgst': order_cgst,
                        'sgst': order_sgst
                    })

                    # Log the detailed breakdown for RES
                    logger.info(f"Order {order.id}: Total {order.total}, Discounted: {order_discounted_total}, SGST: {order_sgst}, CGST: {order_cgst}")

                    # Sum up all totals
                    total = order_total
                    discounted_total = order_discounted_total
                    net_total = order_net_total

                except Order.DoesNotExist:
                    return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            # Generate bill numbers
            bill_no, res_bill_no, hot_bill_no = BillingService.generate_bill_numbers(tenant, bill_type)

            # Create bill
            bill = Bill.objects.create(
                tenant=tenant,
                order_id=order if bill_type == 'RES' else None,
                booking_id=Booking.objects.get(id=booking_id, tenant=tenant) if bill_type == 'HOT' else None,
                total=total,
                discount=room_discount + order_discount + service_discount,  # Total discount for record-keeping
                discounted_amount=discounted_total,
                net_amount=net_total,
                sgst_amount=order_sgst + room_sgst + service_sgst,
                cgst_amount=order_cgst + room_cgst + service_cgst,
                order_sgst=order_sgst,
                order_cgst=order_cgst,
                room_sgst=room_sgst,
                room_cgst=room_cgst,
                service_sgst=service_sgst,
                service_cgst=service_cgst,
                bill_no=bill_no,
                res_bill_no=res_bill_no if bill_type == 'RES' else None,
                hot_bill_no=hot_bill_no if bill_type == 'HOT' else None,
                bill_type=bill_type,
                created_by=request.user
            )

            # Generate GST bill number
            bill.gst_bill_no = BillingService.generate_gst_bill_no(bill_type, bill_no, hot_bill_no if bill_type == 'HOT' else res_bill_no)
            
            bill.save()

            # Serialize the bill and add room, service, and order details
            serializer = self.get_serializer(bill)
            response_data = serializer.data
            response_data['room_details'] = room_details  # Add room details to the response
            response_data['service_details'] = service_details  # Add service details to the response
            response_data['order_details'] = order_details  # Add order details to the response

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
