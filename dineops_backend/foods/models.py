from django.db import models
from django.conf import settings
from accounts.models import Tenant
from datetime import datetime

class FoodItem(models.Model):
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.ImageField(upload_to='foods/images', null=True, blank=True)
    image = models.URLField(null=True, blank=True)  # Store URL instead of image file
    category = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enabled')
    created_at = models.DateTimeField(auto_now_add=True)
    # Temp Fix for existing entries
    # created_at = models.DateTimeField(default=datetime.now)  # Fixed default value
    modified_at = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_food_items')
    modified_by = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name