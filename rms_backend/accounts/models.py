from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    domain_url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_hotel_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_tenant_admin = models.BooleanField(default=False)

# # Temp fix for superuser -- first time only
# class User(AbstractUser):
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
#     is_tenant_admin = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.name
