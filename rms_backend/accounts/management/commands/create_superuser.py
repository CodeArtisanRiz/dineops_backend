from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Tenant

# Get the custom User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with or without a tenant'

    def handle(self, *args, **kwargs):
        # Determine if a tenant is needed
        create_tenant = input('Do you want to create a tenant for this superuser? (yes/no): ').strip().lower()

        tenant = None
        if create_tenant == 'yes':
            # Get tenant information from user input
            tenant_name = input('Enter tenant name: ')
            tenant_domain_url = input('Enter tenant domain URL (optional): ') or None

            # Create a new Tenant object
            tenant, created = Tenant.objects.get_or_create(
                name=tenant_name,
                defaults={'domain_url': tenant_domain_url}
            )

            if not created:
                self.stdout.write(self.style.WARNING(f'Tenant with name "{tenant_name}" already exists.'))

        # Loop until a unique username is provided
        while True:
            username = input('Enter superuser username: ')
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR('Username already exists. Please choose another one.'))
            else:
                break

        # Get superuser email, password, phone, and address
        email = input('Enter superuser email: ')
        password = input('Enter superuser password: ')
        phone = input('Enter superuser phone (optional): ')
        address = input('Enter superuser address (optional): ')

        # Create a new superuser with the provided information
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                phone=phone,
                address=address,
                role='superuser',  # Set the role to 'superuser'
            )

            if tenant:
                user.tenant = tenant
                user.save()
            # Display success message
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {username}{" with tenant "+tenant.name if tenant else ""}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))