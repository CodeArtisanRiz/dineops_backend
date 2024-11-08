from django.core.management.base import BaseCommand
from hotel.models import ServiceUsage
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Truncate the ServiceUsage table and reset related fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Truncating the ServiceUsage table and resetting related fields...')

        with transaction.atomic():
            # Delete all records from the ServiceUsage table
            ServiceUsage.objects.all().delete()

            # Reset the primary key sequence for the ServiceUsage table
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_serviceusage';")

        self.stdout.write(self.style.SUCCESS('Successfully truncated the ServiceUsage table and reset related fields.')) 