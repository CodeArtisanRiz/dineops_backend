from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Tenant

# Get the custom User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with a tenant'

    def handle(self, *args, **kwargs):
        # Get tenant information from user input
        tenant_name = input('Enter tenant name: ')
        tenant_domain_url = input('Enter tenant domain URL: ')
        # Create a new Tenant object
        tenant = Tenant.objects.create(name=tenant_name, domain_url=tenant_domain_url)

        # Loop until a unique username is provided
        while True:
            username = input('Enter superuser username: ')
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR('Username already exists. Please choose another one.'))
            else:
                break

        # Get superuser email and password
        email = input('Enter superuser email: ')
        password = input('Enter superuser password: ')

        # Create a new superuser with the provided information
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            tenant=tenant,
            is_tenant_admin=True
        )
        # Display success message
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {username} with tenant {tenant_name}'))
