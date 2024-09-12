from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

UserModel = get_user_model()

def get_or_create_user(username, email, first_name, last_name, role, phone, address, password, tenant):
    try:
        user = UserModel.objects.get(username=username)
        return user.id
    except ObjectDoesNotExist:
        user = UserModel.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            address=address,
            tenant=tenant
        )
        if not password:
            password = 'defaultpassword'  # Set your default password here
        user.set_password(password)
        user.save()
        return user.id