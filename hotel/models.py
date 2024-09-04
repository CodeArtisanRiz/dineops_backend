from django.db import models
from accounts.models import User, Tenant
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, default='')  # Added field
    beds = models.CharField(max_length=50, default='')  # Added field
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)  # Added field
    images = models.JSONField(default=list, blank=True)  # Added field
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    booked_periods = models.JSONField(default=list, blank=True)  # Store booked time periods

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"

class Booking(models.Model):
    STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Confirmed'),
        (3, 'Cancelled'),
        (4, 'Checked-in'),
        (5, 'Checked-out'),
        (6, 'No-show')
    ]
    ID_CHOICES = [
        (1, 'Single ID for entire booking'),
        (2, 'Single ID per room'),
        (3, 'All guests ID')
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    guests = models.ManyToManyField(User, related_name='bookings', blank=True)
    rooms = models.ManyToManyField(Room, blank=True)
    total_amount_per_booking = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scenario = models.IntegerField(choices=ID_CHOICES, default=1)  # ID scenario choice
    # identification = models.JSONField(blank=True, null=True)
    room_details = models.JSONField(blank=True, null=True)  # Store room-specific data

    def __str__(self):
        return f"Booking {self.id} - Tenant: {self.tenant} - Status: {self.get_status_display()}"

    def save(self, *args, **kwargs):
        logger.debug(f"Saving booking with from_date: {self.from_date}, to_date: {self.to_date}")
        super().save(*args, **kwargs)

# class ServiceCategory(models.Model):
#     name = models.CharField(max_length=50)
#     sub_category = models.CharField(max_length=50, blank=True, null=True)
#     description = models.TextField(blank=True)
#     status = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name


# class Service(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return self.name
