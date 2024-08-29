# hotel/models.py

from django.db import models
from accounts.models import User, Tenant
from django.utils import timezone

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"

class Reservation(models.Model):
    BOOKING_STATUS = (
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    )

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='booked')
    check_in_date = models.DateTimeField(null=True, blank=True)
    check_out_date = models.DateTimeField(null=True, blank=True)
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)
    number_of_guests = models.PositiveIntegerField(default=1) 
    guest_names = models.TextField(blank=True)
    id_image = models.ImageField(upload_to='guest_ids/', blank=True, null=True)

    def __str__(self):
        return f"{self.guest.username} - {self.room.room_number} - {self.status}"
