from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Tenant, Table
from foods.models import FoodItem

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
        ('settled', 'Settled'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    food_items = models.ManyToManyField(FoodItem)
    total_price = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)  # Added discount field
    coupon_used = models.JSONField(default=list, blank=True)  # Added coupon used[] field
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username if self.customer else 'unknown'}"