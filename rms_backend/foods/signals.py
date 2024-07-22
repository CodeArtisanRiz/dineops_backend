from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FoodItem
import datetime

@receiver(pre_save, sender=FoodItem)
def update_modified_at(sender, instance, **kwargs):
    if instance.pk:
        instance.modified_at.append(datetime.datetime.now().isoformat())