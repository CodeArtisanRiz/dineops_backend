from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .services import BillingService
from .serializers import BillSerializer, BillPaymentSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Bill, BillPayment
from django.core.exceptions import PermissionDenied, ValidationError
from decimal import Decimal
from django.db import models
from order.models import Order
from hotel.models import Booking

# Create your views here.

class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bill.objects.filter(tenant=self.request.user.tenant)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            tenant = request.user.tenant
            bill_type = data.get('bill_type')

            if bill_type == 'restaurant':
                order_id = data.get('order')
                if not order_id:
                    return Response(
                        {"error": "Order ID is required"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                order = Order.objects.get(id=order_id, tenant=tenant)
                
                # Calculate order total
                total = BillingService.calculate_order_total(order)
                discount = order.discount or Decimal('0.00')
                
                # Update order with calculated total
                order.total_amount = total - discount
                order.save()
                
                # Prepare bill data
                bill_data = {
                    'bill_type': 'restaurant',
                    'order': order.id,
                    'tenant': tenant.id,
                    'total': total,
                    'discount': discount,
                }

                # Generate bill number
                bill_data['bill_number'] = BillingService.generate_bill_number(tenant)

                # Calculate GST and other amounts
                amounts = BillingService.calculate_bill_amounts(
                    total,
                    discount,
                    tenant,
                    bill_type
                )
                bill_data.update(amounts)

                # Create bill
                serializer = self.get_serializer(data=bill_data)
                serializer.is_valid(raise_exception=True)
                bill = serializer.save(created_by=request.user)

                # Generate GST bill number
                bill.gst_bill_no = BillingService.generate_gst_bill_no(
                    bill.id, 
                    bill.bill_type, 
                    bill.bill_number
                )
                bill.save()

                # Update order status
                order.status = 'billed'
                order.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            elif bill_type == 'hotel':
                booking_id = data.get('booking_id')
                if not booking_id:
                    return Response(
                        {"error": "Booking ID is required for hotel bills"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                booking = Booking.objects.get(id=booking_id, tenant=tenant)

                # Calculate total room charges using the new method
                total_room_charges = booking.calculate_total_room_charges()
                discount = Decimal('0.00')  # Assume no discount for simplicity

                # Prepare bill data
                bill_data = {
                    'bill_type': 'hotel',
                    'booking': booking.id,
                    'tenant': tenant.id,
                    'total': total_room_charges,
                    'discount': discount,
                }

                # Generate bill number
                bill_data['bill_number'] = BillingService.generate_bill_number(tenant)

                # Calculate GST and other amounts
                amounts = BillingService.calculate_bill_amounts(
                    total_room_charges,
                    discount,
                    tenant,
                    bill_type
                )
                bill_data.update(amounts)

                # Create bill
                serializer = self.get_serializer(data=bill_data)
                serializer.is_valid(raise_exception=True)
                bill = serializer.save(created_by=request.user)

                # Generate GST bill number
                bill.gst_bill_no = BillingService.generate_gst_bill_no(
                    bill.id, 
                    bill.bill_type, 
                    bill.bill_number
                )
                bill.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response({"error": "Unsupported bill type"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class BillPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = BillPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BillPayment.objects.filter(bill__tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            # Validate bill belongs to tenant
            bill_id = request.data.get('bill')
            bill = Bill.objects.get(id=bill_id)
            
            if bill.tenant != request.user.tenant:
                raise PermissionDenied("You don't have permission to add payments to this bill")

            # Validate payment amount
            amount = Decimal(request.data.get('amount', 0))
            remaining = bill.net_amount - bill.payments.aggregate(
                total=models.Sum('amount')
            )['total'] or bill.net_amount

            if amount <= 0:
                raise ValidationError("Payment amount must be greater than zero")
            
            if amount > remaining:
                raise ValidationError(f"Payment amount ({amount}) exceeds remaining amount ({remaining})")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Bill.DoesNotExist:
            return Response(
                {"error": "Bill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, PermissionDenied) as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
