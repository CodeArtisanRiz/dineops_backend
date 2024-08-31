from django.db import models
from accounts.models import User, Tenant
from django.utils import timezone


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

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"
    

# class Booking(models.Model):
#     STATUS_CHOICES = [
#         (1, 'Pending'),
#         (2, 'Confirmed'),
#         (3, 'Cancelled'),
#         (4, 'Checked-in'),
#         (5, 'Checked-out'),
#         (6, 'No-show'),
#     ]
#     ID_CHOICES = [
#         (1, 'Single ID for entire booking.'),
#         (2, 'Single ID per room'),
#         (3, 'All guests ID'),
#     ]
#     PAYMENT_CHOICES = [
#         (1, 'Cash'),
#         (2, 'Credit Card'),
#         (3, 'Debit Card'),
#         (4, 'UPI'),
#         (5, 'Other'),
#     ]

#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
#     room = models.ManyToManyField(Room)
    
#     booking_date = models.DateTimeField(default=timezone.now)
#     from_date = models.DateField()
#     to_date = models.DateField()
#     status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    
#     guest_count = models.IntegerField(default=1)
#     guests = models.ManyToManyField(User)  # Guests linked to User model
#     identification = models.JSONField(blank=True)  # Store ID details (e.g., {"guest_id": "ID123"})
#     phone = models.JSONField(blank=True)  # Store phone numbers (e.g., {"guest_1": "1234567890"})
#     email = models.JSONField(blank=True)  # Store emails (e.g., {"guest_1": "email@example.com"})
#     address = models.JSONField(blank=True)  # Store addresses (e.g., {"guest_1": "Address"})
    
#     check_in = models.DateTimeField(null=True, blank=True)
#     check_out = models.DateTimeField(null=True, blank=True)

#     amount_breakdown = models.JSONField(blank=True)  # Store price breakdown (e.g., {"room": 1000, "services": 200})
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, blank=True)
    
#     scenario = models.IntegerField(choices=ID_CHOICES, default=1)  # Scenario for ID handling
    
#     def __str__(self):
#         return f"Booking on {self.tenant} - {self.booking_date} (Scenario: {self.get_scenario_display()})"