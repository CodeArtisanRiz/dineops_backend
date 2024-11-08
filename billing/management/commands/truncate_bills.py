from django.core.management.base import BaseCommand
from billing.models import Bill, BillPayment
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Truncate the Bill table and reset related fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Truncating the Bill table and resetting related fields...')

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Delete all records from the BillPayment table first to avoid foreign key constraint issues
            BillPayment.objects.all().delete()

            # Delete all records from the Bill table
            Bill.objects.all().delete()

            # Reset the primary key sequence for the Bill table
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='billing_bill';")

            # Reset the primary key sequence for the BillPayment table
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='billing_billpayment';")

        self.stdout.write(self.style.SUCCESS('Successfully truncated the Bill table and reset related fields.')) 