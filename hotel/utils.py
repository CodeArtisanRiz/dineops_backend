from accounts.models import User
from .models import Room
import logging
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

def get_or_create_user(guest_data, tenant):
    phone = guest_data.get('phone')
    username = f"{tenant.id}_{phone}"  # Set username to tenant+phone
    user, created = User.objects.get_or_create(username=username, defaults={
        'first_name': guest_data.get('first_name'),
        'last_name': guest_data.get('last_name'),
        'dob': guest_data.get('dob'),
        'address': guest_data.get('address'),
        'phone': phone,
        'tenant': tenant,
        'role': 'guest'  # Set role to 'guest'
    })
    if not created:
        # Update existing user with new data
        user.first_name = guest_data.get('first_name')
        user.last_name = guest_data.get('last_name')
        user.dob = guest_data.get('dob')
        user.address = guest_data.get('address')
        user.phone = phone
        user.tenant = tenant
        user.role = 'guest'
        user.save()
    return user, created

def assign_rooms_to_booking(rooms_data, booking):
    for room in rooms_data:
        room.status = 'occupied'
        room.save()
        booking.rooms.add(room)