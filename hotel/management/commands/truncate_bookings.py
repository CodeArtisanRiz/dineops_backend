from django.core.management.base import BaseCommand
from hotel.models import Booking, RoomBooking, CheckIn, CheckOut
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Truncate the Booking table and reset related fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Truncating the Booking, CheckIn, and CheckOut tables and resetting related fields...')

        with transaction.atomic():
            # Delete related RoomBooking, CheckIn, and CheckOut records first
            CheckOut.objects.all().delete()
            CheckIn.objects.all().delete()
            RoomBooking.objects.all().delete()

            # Delete all records from the Booking table
            Booking.objects.all().delete()

            # Reset the primary key sequence for the Booking, CheckIn, and CheckOut tables
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_booking';")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_checkin';")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_checkout';")

        self.stdout.write(self.style.SUCCESS('Successfully truncated the Booking, CheckIn, and CheckOut tables and reset related fields.')) 