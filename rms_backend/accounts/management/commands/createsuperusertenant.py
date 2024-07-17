from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Tenant

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with a tenant'

    def handle(self, *args, **kwargs):
        tenant_name = input('Enter tenant name: ')
        tenant_domain_url = input('Enter tenant domain URL: ')
        tenant = Tenant.objects.create(name=tenant_name, domain_url=tenant_domain_url)

        while True:
            username = input('Enter superuser username: ')
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR('Username already exists. Please choose another one.'))
            else:
                break

        email = input('Enter superuser email: ')
        password = input('Enter superuser password: ')

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            tenant=tenant,
            is_tenant_admin=True
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {username} with tenant {tenant_name}'))
