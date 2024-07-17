from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Tenant(models.Model):
    # Name of the tenant
    name = models.CharField(max_length=100)
    # Unique URL for the tenant's domain
    domain_url = models.URLField(unique=True)
    # Timestamp for when the tenant was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Flag to indicate if the tenant has access to hotel features
    has_hotel_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Foreign key relationship to the Tenant model
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # Flag to indicate if the user is an admin for their tenant
    is_tenant_admin = models.BooleanField(default=False)



# Temp fix for superuser -- first time only
# class User(AbstractUser):
#     # Optional foreign key relationship to the Tenant model for superuser
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
#     # Flag to indicate if the user is an admin for their tenant
#     is_tenant_admin = models.BooleanField(default=False)

