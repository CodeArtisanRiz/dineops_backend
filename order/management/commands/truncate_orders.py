from django.core.management.base import BaseCommand
from order.models import Order
from foods.models import Table
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Truncate the Order table and reset all tables'

    def handle(self, *args, **kwargs):
        self.stdout.write('Truncating the Order table and resetting all tables...')

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Delete all records from the Order table
            Order.objects.all().delete()

            # Reset the primary key sequence
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='order_order';")

            # Reset all tables: set occupied to False and order to None
            Table.objects.update(occupied=False, order=None)

        self.stdout.write(self.style.SUCCESS('Successfully truncated the Order table and reset all tables.')) 