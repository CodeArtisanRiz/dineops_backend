from django.db import models
from django.db.models import Max
from accounts.models import Tenant, User
from hotel.models import Booking
from order.models import Order
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class Bill(models.Model):
    BILL_TYPE_CHOICES = [
        ('HOT', 'Hotel'),
        ('RES', 'Restaurant'),
    ]
    
    STATUS_CHOICES = [
        ('cancelled', 'Cancelled'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    res_bill_no = models.IntegerField(null=True, blank=True)
    hot_bill_no = models.IntegerField(null=True, blank=True)
    bill_no = models.IntegerField(null=True, blank=True)
    gst_bill_no = models.CharField(max_length=100, null=True, blank=True)
    bill_type = models.CharField(max_length=3, choices=BILL_TYPE_CHOICES)
    customer_gst = models.CharField(max_length=15, null=True, blank=True)
    
    # Order or Booking reference
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    booking_id = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Amounts
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # GST breakdown
    room_sgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    room_cgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_sgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_cgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_sgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_cgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Totals
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.bill_no} - {self.bill_type} - {self.net_amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class BillPayment(models.Model):
    """Track individual payments against a bill"""

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('other', 'Other'),
    ]
    bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    bill_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    paid_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_details = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='payments_created'
    )

    def save(self, *args, **kwargs):
        payment_status = kwargs.pop('payment_status', 'partial')  # Default to 'partial' if not provided
        super().save(*args, **kwargs)
        self.update_bill_status(payment_status)

    def update_bill_status(self, payment_status):
        # Use self.bill_id to access the related Bill object
        if payment_status == 'paid':
            self.bill_id.status = 'paid'
            
            if self.bill_id.bill_type == 'RES':
                # Update the status of the related Order to 'settled'
                order = self.bill_id.order_id
                if order:
                    order.status = 'settled'
                    order.save()
            
            elif self.bill_id.bill_type == 'HOT':
                # Update the status of all related Orders to 'settled'
                booking = self.bill_id.booking_id
                if booking:
                    orders = Order.objects.filter(booking_id=booking.id)
                    for order in orders:
                        order.status = 'settled'
                        order.save()
        else:
            self.bill_id.status = 'partial'
        
        self.bill_id.save()

    def __str__(self):
        return f"Payment of {self.paid_amount} for {self.bill_id.bill_no}"
