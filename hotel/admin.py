from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'price', 'status', 'is_available')
    list_filter = ('status', 'is_available')
    search_fields = ('room_number', 'room_type')
