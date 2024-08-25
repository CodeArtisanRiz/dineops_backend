from django.contrib import admin
from .models import Room, Reservation, RoomHistory

admin.site.register(Room)
# admin.site.register(GuestProfile)
admin.site.register(Reservation)
admin.site.register(RoomHistory)