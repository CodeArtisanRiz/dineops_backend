from accounts.models import User
from .models import Room
import logging

logger = logging.getLogger(__name__)

def get_or_create_user(guest_data):
    dob = guest_data['dob'].strftime('%d-%m-%Y')  # Format the date of birth
    existing_user = User.objects.filter(username=guest_data['phone']).first()
    if existing_user:
        logger.info("User with phone number %s already exists", guest_data['phone'])
        return existing_user, False
    else:
        guest_user = User.objects.create_user(
            username=guest_data['phone'],
            password=dob,  # Use formatted date of birth as password
            first_name=guest_data['first_name'],
            last_name=guest_data['last_name'],
            address=guest_data['address'],
            role='guest'  # Explicitly set the role to 'guest'
        )
        return guest_user, True

def assign_rooms_to_booking(rooms_data, booking):
    for room in rooms_data:
        room.status = 'occupied'
        room.save()
        booking.rooms.add(room)