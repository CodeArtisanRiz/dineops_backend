from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Tenant
from foods.models import FoodItem, Table
from hotel.models import Room

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('kot', 'Kot'),
        ('served', 'Served'),
        ('billed', "Billed"),
        # ('completed', 'Completed'),
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
    order_type = models.CharField(max_length=20, choices=ORDER_CHOICES, default='dine_in')
    tables = models.ManyToManyField(Table, blank=True, related_name='orders')  # Add this line
    # room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    food_items = models.ManyToManyField(FoodItem)
    quantity = models.JSONField(default=list, blank=True)
    total_price = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)  # Added discount field
    coupon_used = models.JSONField(default=list, blank=True)  # Added coupon used[] field
    notes = models.TextField(null=True, blank=True)

    kot_count = models.IntegerField(default=0)

    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    def __str__(self):
        return f"Order {self.id} by {self.customer.username if self.customer else 'unknown'}"