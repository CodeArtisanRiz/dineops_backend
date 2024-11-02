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
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
    ]
    
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=50)
    gst_bill_no = models.CharField(max_length=100, null=True, blank=True)
    bill_type = models.CharField(max_length=20)
    
    # Order or Booking reference
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Amounts
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # GST breakdown
    room_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totals
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        # return self.bill_number
        return f"{self.bill_number} - {self.bill_type} - {self.net_amount}"


class BillPayment(models.Model):
    """Track individual payments against a bill"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_method = models.CharField(max_length=20, choices=Bill.PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_details = models.JSONField(null=True, blank=True)  # Store transaction IDs, etc.
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='payments_created'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update bill status based on payments
        total_paid = self.bill.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        if total_paid >= self.bill.net_amount:
            self.bill.status = 'paid'
        elif total_paid > 0:
            self.bill.status = 'partial'
        else:
            self.bill.status = 'unpaid'
            
        self.bill.save()

    def __str__(self):
        return f"Payment of {self.amount} for {self.bill.bill_number}"
