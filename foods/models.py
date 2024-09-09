from django.db import models
from django.conf import settings
from accounts.models import Tenant

class Category(models.Model):
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.JSONField(default=list, blank=True)  # Store list of URLs instead of a single URL
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enabled')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_categories')
    modified_by = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.JSONField(default=list)  # Store list of URLs instead of a single URL
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='food_items')
    veg = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enabled')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_food_items')
    modified_by = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name