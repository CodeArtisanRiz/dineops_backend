from django.db import models
from django.contrib.auth.models import AbstractUser

class Tenant(models.Model):
    tenant_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    has_hotel_feature = models.BooleanField(default=False)

    total_tables = models.IntegerField(default=0)

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
    gst_no = models.CharField(max_length=15, null=True, blank=True)
    # Preferences and settings
    logo = models.JSONField(default=list)  # Changed from URLField to JSONField
    # Other
    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)

    # Restaurant GST rates
    restaurant_cgst = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=2.50,
        help_text="Restaurant CGST rate in percentage"
    )
    restaurant_sgst = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=2.50,
        help_text="Restaurant SGST rate in percentage"
    )

    # Hotel Room GST rates
    hotel_cgst_lower = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=6.00,
        help_text="Hotel CGST rate for rooms below limit margin"
    )
    hotel_sgst_lower = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=6.00,
        help_text="Hotel SGST rate for rooms below limit margin"
    )
    hotel_cgst_upper = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=9.00,
        help_text="Hotel CGST rate for rooms above limit margin"
    )
    hotel_sgst_upper = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=9.00,
        help_text="Hotel SGST rate for rooms above limit margin"
    )
    
    # Service GST rates
    service_cgst_lower = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=9.00,
        help_text="Service CGST rate for services below limit margin"
    )
    service_sgst_lower = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=9.00,
        help_text="Service SGST rate for services below limit margin"
    )
    service_cgst_upper = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=14.00,
        help_text="Service CGST rate for services above limit margin"
    )
    service_sgst_upper = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=14.00,
        help_text="Service SGST rate for services above limit margin"
    )
    
    # Price thresholds
    hotel_gst_limit_margin = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=7500.00,
        help_text="Price threshold for different room GST rates"
    )
    service_gst_limit_margin = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        help_text="Price threshold for different service GST rates (if null, lower rate applies)"
    )

    subscription_from = models.DateField(null=True, blank=True)  # New field
    subscription_to = models.DateField(null=True, blank=True)  # New field

    def __str__(self):
        return self.tenant_name



class User(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'), # Restaurant Customer User.
        ('guest', 'Guest'), # Hotel Guest User.
    ]
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    # is_tenant_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    # address = models.TextField(blank=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)
    # identification = models.JSONField(default=list, blank=True)  # Remove this field

    def __str__(self):
        return self.username