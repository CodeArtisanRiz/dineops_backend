# hotel/models.py

from django.db import models
from django.utils import timezone

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Maintenance'),
    ]
    number = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    bookings = models.JSONField(default=list)
    past_bookings = models.JSONField(default=list)

    def __str__(self):
        return f"Room {self.number} ({self.type}) - {self.status}"


class Reservation(models.Model):
    guest_name = models.CharField(max_length=100)
    check_in_date = models.DateTimeField(null=True, blank=True)
    check_out_date = models.DateTimeField(null=True, blank=True)
    rooms = models.ManyToManyField(Room, related_name='reservations')
    booking_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reservation for {self.guest_name} on {self.booking_date}"

    def check_out(self):
        # Move current bookings to past bookings
        for room in self.rooms.all():
            booking_detail = {
                'guest_name': self.guest_name,
                'check_in_date': self.check_in_date.isoformat(),
                'check_out_date': self.check_out_date.isoformat(),
            }
            room.bookings = [b for b in room.bookings if b != booking_detail]
            room.past_bookings.append(booking_detail)
            room.save()
