from decimal import Decimal
from django.db.models import Max
from billing.models import Bill

class BillingService:
    @staticmethod
    def generate_bill_number(tenant):
        last_bill = Bill.objects.filter(tenant=tenant).aggregate(Max('bill_number'))
        last_number = last_bill['bill_number__max']
        
        if last_number:
            sequence = int(last_number.split('/')[-1]) + 1
        else:
            sequence = 1
        
        return f"{tenant.tenant_name}/{sequence}"

    @staticmethod
    def generate_gst_bill_no(bill_id, bill_type, bill_number):
        return f"{bill_id}/{bill_type}/{bill_number}"

    @staticmethod
    def calculate_restaurant_gst(amount, tenant):
        """Calculate GST for restaurant orders"""
        sgst = round(amount * (tenant.restaurant_sgst / 100), 2)
        cgst = round(amount * (tenant.restaurant_cgst / 100), 2)
        return sgst, cgst

    @staticmethod
    def calculate_room_gst_per_day(room_rate, tenant):
        """Calculate GST for a single room for one day"""
        if room_rate <= tenant.hotel_gst_limit_margin:
            sgst = round(room_rate * (tenant.hotel_sgst_lower / 100), 2)
            cgst = round(room_rate * (tenant.hotel_cgst_lower / 100), 2)
        else:
            sgst = round(room_rate * (tenant.hotel_sgst_upper / 100), 2)
            cgst = round(room_rate * (tenant.hotel_cgst_upper / 100), 2)
        return sgst, cgst

    @staticmethod
    def calculate_service_gst(service_charge, tenant):
        """Calculate GST for services based on threshold"""
        # If no margin is set or charge is below margin, use lower rate
        if not tenant.service_gst_limit_margin or service_charge <= tenant.service_gst_limit_margin:
            sgst = round(service_charge * (tenant.service_sgst_lower / 100), 2)
            cgst = round(service_charge * (tenant.service_cgst_lower / 100), 2)
        else:
            sgst = round(service_charge * (tenant.service_sgst_upper / 100), 2)
            cgst = round(service_charge * (tenant.service_cgst_upper / 100), 2)
        return sgst, cgst

    @staticmethod
    def calculate_order_total(order):
        """Calculate total amount from order items"""
        if not order.total:
            order.calculate_totals()
        return order.total or Decimal('0.00')

    @staticmethod
    def calculate_bill_amounts(sub_total, discount, tenant, bill_type):
        """Calculate all bill amounts based on bill type"""
        # Convert to Decimal if not already
        sub_total = Decimal(str(sub_total))
        discount = Decimal(str(discount))
        discounted_amount = sub_total - discount

        result = {
            'discounted_amount': discounted_amount,
            'room_sgst': Decimal('0.00'),
            'room_cgst': Decimal('0.00'),
            'order_sgst': Decimal('0.00'),
            'order_cgst': Decimal('0.00'),
            'service_sgst': Decimal('0.00'),
            'service_cgst': Decimal('0.00'),
            'sgst_amount': Decimal('0.00'),
            'cgst_amount': Decimal('0.00'),
            'net_amount': Decimal('0.00')
        }

        if bill_type == 'restaurant':
            # Calculate restaurant GST
            result['order_sgst'], result['order_cgst'] = BillingService.calculate_restaurant_gst(
                discounted_amount, 
                tenant
            )
            result['sgst_amount'] = result['order_sgst']
            result['cgst_amount'] = result['order_cgst']
            result['net_amount'] = discounted_amount + result['sgst_amount'] + result['cgst_amount']

        return result

    @staticmethod
    def get_bill_details(bill):
        """Get itemized bill details"""
        details = {
            'items': [],
            'summary': {
                'sub_total': bill.sub_total,
                'discount': bill.discount,
                'sgst_amount': bill.sgst_amount,
                'cgst_amount': bill.cgst_amount,
                'net_amount': bill.net_amount
            }
        }

        if bill.bill_type == 'restaurant':
            # Add order details
            if bill.order:
                details['items'].append({
                    'type': 'order',
                    'items': bill.order.items,
                    'total': bill.order.total_amount
                })

        elif bill.bill_type == 'hotel':
            # Add room charges
            if bill.booking:
                details['items'].append({
                    'type': 'room',
                    'room_numbers': [room.room_number for room in bill.booking.rooms.all()],
                    'check_in': bill.booking.check_in,
                    'check_out': bill.booking.check_out,
                    'total': bill.booking.total_room_charges
                })

                # Add order details if any
                if hasattr(bill.booking, 'orders') and bill.booking.orders.exists():
                    for order in bill.booking.orders.all():
                        details['items'].append({
                            'type': 'order',
                            'items': order.items,
                            'total': order.total_amount
                        })

                # Service details will be added later

        return details