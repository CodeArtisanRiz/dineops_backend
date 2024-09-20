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
    image = models.JSONField(default=list, blank=True)  # Added field
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Confirmed'),
        (3, 'Cancelled'),
        (4, 'Checked-in'),
        (5, 'Checked-out'),
        (6, 'No-show')
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    guests = models.ManyToManyField(User, related_name='bookings', blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - Tenant: {self.tenant} - Status: {self.get_status_display()}"

class RoomBooking(models.Model):
    STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Confirmed'),
        (3, 'Checked-in'),
        (4, 'Checked-out'),
        (5, 'Cancelled')
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    is_active = models.BooleanField(default=True)  # Added field

    def __str__(self):
        return f"RoomBooking {self.id} - Room: {self.room.room_number} - Status: {self.get_status_display()}"

class CheckIn(models.Model):
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE)
    check_in_date = models.DateTimeField(default=timezone.now)
    checked_in_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"CheckIn {self.id} - RoomBooking: {self.room_booking.id}"

class CheckOut(models.Model):
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE)
    check_out_date = models.DateTimeField(default=timezone.now)
    checked_out_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"CheckOut {self.id} - RoomBooking: {self.room_booking.id}"

class ServiceUsage(models.Model):
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    usage_date = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"ServiceUsage {self.id} - RoomBooking: {self.room_booking.id} - Service: {self.service.name}"

class Billing(models.Model):
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE)
    billing_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    details = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Billing {self.id} - RoomBooking: {self.room_booking.id}"

class Payment(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.id} - Billing: {self.billing.id}"
