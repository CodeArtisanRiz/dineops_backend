from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Bill
from .serializers import BillSerializer
from .services import BillingService
from order.models import Order
from hotel.models import Booking
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

            if bill_type == 'RES':
                total, discounted_total, net_total, order_sgst, order_cgst = self.order_bill_calc(
                    order_instance, discount, tenant
                )

            if bill_type == 'HOT':
                total, discounted_total, net_total, order_sgst, order_cgst = self.service_bill_calc(
                    booking_id, discount, tenant
                )
                room_total, room_discounted_total, room_net_total = self.rooms_bill_calc(
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
                sgst_amount=order_sgst,
                cgst_amount=order_cgst,
                order_sgst=order_sgst,
                order_cgst=order_cgst,
                bill_no=bill_no,
                res_bill_no=res_bill_no if bill_type == 'RES' else None,
                hot_bill_no=hot_bill_no if bill_type == 'HOT' else None,
                bill_type=bill_type,
                created_by=request.user
            )

            # Generate GST bill number
            bill.gst_bill_no = BillingService.generate_gst_bill_no(bill_type, res_bill_no or hot_bill_no, bill.id)
            bill.save()

            serializer = self.get_serializer(bill)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    def order_bill_calc(self, order_instance, discount, tenant):
        """Calculate totals, discounts, and GST amounts for a single order."""
        total = order_instance.total  # Assuming this field exists

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

        # Fetch associated orders for the booking
        associated_orders = Order.objects.filter(booking=booking, tenant=tenant)
        for order in associated_orders:
            total += order.total  # Add each order's total to the bill total

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
        total = booking.room_charges  # Assuming this field exists

        # Calculate discounted total
        discounted_total = total - discount

        # Calculate net total (assuming no GST for room charges in this example)
        net_total = discounted_total

        return total, discounted_total, net_total
