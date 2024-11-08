from django.core.management.base import BaseCommand
from hotel.models import Service, ServiceCategory, ServiceUsage
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Truncate the Service and ServiceCategory tables and reset related fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Truncating the Service and ServiceCategory tables and resetting related fields...')

        with transaction.atomic():
            # Delete related ServiceUsage records first
            ServiceUsage.objects.all().delete()

            # Delete all records from the Service table
            Service.objects.all().delete()

            # Delete all records from the ServiceCategory table
            ServiceCategory.objects.all().delete()

            # Reset the primary key sequence for the Service table
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_service';")

            # Reset the primary key sequence for the ServiceCategory table
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='hotel_servicecategory';")

        self.stdout.write(self.style.SUCCESS('Successfully truncated the Service and ServiceCategory tables and reset related fields.')) 