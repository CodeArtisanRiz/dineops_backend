from django.db import models
from django.contrib.auth.models import AbstractUser

class Tenant(models.Model):
    # Primary
    tenant_name = models.CharField(max_length=100)
    has_hotel_feature = models.BooleanField(default=False)
    gst_no = models.CharField(max_length=15, null=True, blank=True)
    logo = models.JSONField(default=list)
    fssai = models.JSONField(default=list)
    hsn = models.JSONField(default=list)
    # Address
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pin = models.CharField(max_length=20, null=True, blank=True)
    # Contact
    phone = models.CharField(max_length=10, null=True, blank=True)
    alt_phone = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
   
    # GST
    gst_threshold = models.DecimalField(max_digits=10,decimal_places=2,default=7500.00)
    room_cgst = models.DecimalField(max_digits=4,decimal_places=2,default=6.00)
    room_sgst = models.DecimalField(max_digits=4,decimal_places=2,default=6.00)
    room_cgst_premium = models.DecimalField(max_digits=4,decimal_places=2,default=9.00)
    room_sgst_premium = models.DecimalField(max_digits=4,decimal_places=2,default=9.00)
    
    food_cgst = models.DecimalField(max_digits=4,decimal_places=2, default=2.50)
    food_sgst = models.DecimalField(max_digits=4,decimal_places=2,default=2.50)
    food_cgst_premium = models.DecimalField(max_digits=4,decimal_places=2, default=9.00)
    food_sgst_premium = models.DecimalField(max_digits=4,decimal_places=2,default=9.00)


    service_cgst = models.DecimalField(max_digits=4,decimal_places=2,default=9.00)
    service_sgst = models.DecimalField(max_digits=4,decimal_places=2,default=9.00)
     # Other
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.JSONField(default=list, blank=True)
    modified_by = models.JSONField(default=list, blank=True)
    # Subscription
    # subscription_from = models.DateField(null=True, blank=True)
    # subscription_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.tenant_name



class User(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
        ('guest', 'Guest'),
    ]
    # Primary
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_verified = models.BooleanField(default=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    dob = models.DateField(null=True, blank=True)
    # Contact
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    # Address
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pin = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username


class PhoneVerification(models.Model):
    phone = models.CharField(max_length=15)
    verification_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'verification_id']),
        ]