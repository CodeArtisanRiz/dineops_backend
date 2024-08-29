from django.contrib import admin
from .models import Room, Reservation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'price', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number', 'room_type')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'status', 'check_in_date', 'check_out_date')
    list_filter = ('status', 'room')
    search_fields = ('guest__username', 'room__room_number')
