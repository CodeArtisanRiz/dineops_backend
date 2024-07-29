from django.db import models
from django.contrib.auth.models import AbstractUser

class Tenant(models.Model):
    tenant_name = models.CharField(max_length=100)
    domain_url = models.URLField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_hotel_feature = models.BooleanField(default=False)

    # Address details
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pin = models.CharField(max_length=20, null=True, blank=True)

    # Contact information
    phone = models.CharField(max_length=10, null=True, blank=True)
    alt_phone = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    # Additional business information
    gst_in = models.CharField(max_length=15, null=True, blank=True)
    # Preferences and settings
    logo_url = models.URLField(null=True, blank=True)
    # Other
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tenant_name

class Table(models.Model):
    tenant = models.ForeignKey(Tenant, related_name='tables', on_delete=models.CASCADE)
    table_number = models.PositiveIntegerField(default=0)
    occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.table_number} - {'Occupied' if self.occupied else 'Free'}"

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    ]
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    # is_tenant_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.username