from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

UserModel = get_user_model()

def get_or_create_user(
    username, email, first_name, last_name, role, phone,
    address_line_1, address_line_2, city, state, country, pin,
    password, tenant
):
    try:
        user = UserModel.objects.get(username=username)
        # Update user details if they are incorrect
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        user.phone = phone
        user.address_line_1 = address_line_1
        user.address_line_2 = address_line_2
        user.tenant = tenant
        if password:
            user.set_password(password)
        user.city = city
        user.state = state
        user.country = country
        user.pin = pin
        user.save()
        return user.id
    except UserModel.DoesNotExist:  # Changed from User.DoesNotExist
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            country=country,
            pin=pin,
            tenant=tenant
        )
        if not password:
            password = 'defaultpassword'  # Set your default password here
        user.set_password(password)
        user.save()
        return user.id