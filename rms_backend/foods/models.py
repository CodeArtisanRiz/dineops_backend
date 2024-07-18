from django.db import models
from accounts.models import Tenant

class FoodItem(models.Model):
    # Tenant who owns this food item
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # Name of the food item
    name = models.CharField(max_length=255)
    # Description of the food item
    description = models.TextField()
    # Price of the food item
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Image of the food item (optional)
    image = models.ImageField(upload_to='foods/', null=True, blank=True)

    def __str__(self):
        return self.name
