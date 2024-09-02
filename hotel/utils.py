from accounts.models import User
from .models import Room
import logging

logger = logging.getLogger(__name__)

def get_or_create_user(guest_data):
    user, created = User.objects.get_or_create(
        id=guest_data.get('id'),
        defaults={
            'first_name': guest_data.get('first_name'),
            'last_name': guest_data.get('last_name'),
            'phone': guest_data.get('phone'),
            'dob': guest_data.get('dob'),
            'address': guest_data.get('address'),
        }
    )
    if created:
        logger.info(f"Created new user: {user.id}")
        # Use a temporary variable to store dob as a string for password creation
        dob_str = guest_data.get('dob').strftime('%Y%m%d') if guest_data.get('dob') else 'defaultpassword'
        user.set_password(dob_str)
        user.save()
    else:
        logger.info(f"Found existing user: {user.id}")
    return user, created

def assign_rooms_to_booking(rooms_data, booking):
    for room in rooms_data:
        room.status = 'occupied'
        room.save()
        booking.rooms.add(room)