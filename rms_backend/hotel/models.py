from django.db import models
from accounts.models import Tenant, User
from django.utils import timezone

class Room(models.Model):
    ROOM_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='available')
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

class Reservation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    guest = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.guest.username} - {self.room.name}"

class RoomHistory(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.reservation.guest.username} - {self.room.name}"