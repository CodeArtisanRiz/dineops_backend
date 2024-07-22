from django.db import models
from django.contrib.auth.models import AbstractUser

class Tenant(models.Model):
    tenant_name = models.CharField(max_length=100)
    domain_url = models.URLField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_hotel_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.tenant_name  # Fixed typo: self.name to self.tenant_name

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