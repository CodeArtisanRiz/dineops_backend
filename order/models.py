from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Tenant
from foods.models import FoodItem, Table
from hotel.models import Room, Booking
from decimal import Decimal

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('kot', 'Kot'),
        ('served', 'Served'),
        ('billed', "Billed"),
        ('settled', "Setted"),
        ('cancelled', 'Cancelled')

    ]
    ORDER_CHOICES = [
        ('take_away', 'Take Away'),
        ('dine_in', 'Dine In'),
        ('delivery', 'Delivery'),
        ('online', 'Online'),
        ('hotel', 'Hotel')
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('due', 'Due'),
        ('other', 'Other')
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    order_type = models.CharField(max_length=20, choices=ORDER_CHOICES, default='dine_in')
    tables = models.ManyToManyField(Table, blank=True, related_name='orders')
    room_id = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    booking_id = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    food_items = models.ManyToManyField(FoodItem)
    quantity = models.JSONField(default=list, blank=True)
    notes = models.TextField(null=True, blank=True)
    kot_count = models.IntegerField(default=0)
    

    # payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True)
    # total_price = models.DecimalField(null=True, max_digits=10, decimal_places=2)  # Added discount field
    # coupon_used = models.JSONField(default=list, blank=True)  # Added coupon used[] field
    # Add new price-related fields
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Renamed from sub_total
    # discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # net_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # total - discount

    

    def save(self, *args, **kwargs):
        # Calculate totals before saving
        # self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.status}"