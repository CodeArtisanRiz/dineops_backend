from django.contrib import admin
from .models import Room
# , Reservation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'type', 'status', 'price']

# @admin.register(Reservation)
# class ReservationAdmin(admin.ModelAdmin):
#     list_display = ['guest_name', 'check_in_date', 'check_out_date', 'booking_date']
