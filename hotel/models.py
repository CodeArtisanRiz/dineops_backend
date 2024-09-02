from django.db import models
from accounts.models import User, Tenant
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    booking_id = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_rooms', default=None)

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
    PAYMENT_CHOICES = [
        (1, 'Cash'),
        (2, 'Credit Card'),
        (3, 'Debit Card'),
        (4, 'UPI'),
        (5, 'Other')
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    guests = models.ManyToManyField(User, related_name='bookings', blank=True)
    rooms = models.ManyToManyField(Room, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.IntegerField(choices=PAYMENT_CHOICES, default=1)
    scenario = models.IntegerField(choices=ID_CHOICES, default=1)  # ID scenario choice
    identification = models.JSONField(blank=True, null=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - Tenant: {self.tenant} - Status: {self.get_status_display()}"

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
