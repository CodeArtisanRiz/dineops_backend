import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Booking, Room
from accounts.models import Tenant, User
from .serializers import RoomSerializer
from django.contrib.auth import get_user_model
from .serializers import BookingSerializer
from django.db import transaction



logger = logging.getLogger(__name__)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Room.objects.all()
        return Room.objects.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            tenant_id = self.request.data.get('tenant')
            if not tenant_id:
                raise ValidationError("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            serializer.save(tenant=tenant)
        else:
            serializer.save(tenant=user.tenant)

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_superuser:
            tenant_id = self.request.data.get('tenant')
            if tenant_id:
                tenant = get_object_or_404(Tenant, id=tenant_id)
                serializer.save(tenant=tenant)
            else:
                serializer.save()
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        if not user.is_superuser and instance.tenant != user.tenant:
            raise ValidationError("You do not have permission to delete this room.")
        room_number = instance.room_number
        self.perform_destroy(instance)
        return Response({"message": f"Room - {room_number} deleted"}, status=status.HTTP_204_NO_CONTENT)



logger = logging.getLogger(__name__)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                logger.info("Received booking request")
                # Validate request data
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                logger.info("Booking data validated successfully")

                # Extract the validated data
                validated_data = serializer.validated_data
                guests_data = validated_data.pop('guests')
                scenario = validated_data.get('scenario', 1)
                tenant = self.get_tenant_from_request(request)

                total_amount = 0

                # Create the booking instance
                booking = Booking.objects.create(tenant=tenant, **validated_data)
                logger.info(f"Booking created: {booking}")

                # Handle guest creation, room assignment, and services
                for guest_data in guests_data:
                    rooms = guest_data.pop('rooms')
                    services = guest_data.pop('services', [])
                    identification = guest_data.pop('identification', None)

                    # Create guest user
                    guest_user = self.create_guest_user(guest_data)
                    booking.guests.add(guest_user)

                    # Assign rooms and calculate total amounts
                    guest_total = self.assign_rooms_and_services(booking, guest_user, rooms, services)
                    total_amount += guest_total

                    # Handle identification based on scenario
                    self.assign_identification(booking, guest_user, rooms, identification, scenario)
                    logger.info(f"Guest added: {guest_user.username} with rooms and services")

                # Finalize booking total and save
                booking.total_amount = total_amount
                booking.save()
                logger.info(f"Booking finalized with total amount: {total_amount}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_tenant_from_request(self, request):
        user = request.user
        if user.is_superuser:
            tenant_id = request.data.get('tenant')
            if not tenant_id:
                raise ValidationError("Superuser must provide tenant ID.")
            tenant = Tenant.objects.get(id=tenant_id)
        else:
            tenant = user.tenant
        logger.info(f"Tenant resolved: {tenant}")
        return tenant

    def create_guest_user(self, guest_data):
        guest_user = User.objects.create_user(
            username=guest_data['phone'],
            password=guest_data['dob'],  # Simplified for demo
            role='guest',
            first_name=guest_data['first_name'],
            last_name=guest_data['last_name'],
            dob=guest_data['dob'],
            address=guest_data['address'],
            phone=guest_data['phone']
        )
        logger.info(f"Guest user created: {guest_user.username}")
        return guest_user

    def assign_rooms_and_services(self, booking, guest_user, rooms, services):
        total_guest_amount = 0

        # Assign rooms to the guest and update room statuses
        for room in rooms:
            room_instance = Room.objects.get(id=room)
            room_instance.status = 'occupied'
            room_instance.save()
            booking.rooms.add(room_instance)
            total_guest_amount += room_instance.price
            logger.info(f"Room assigned: {room_instance.room_number} to guest: {guest_user.username}")

        # Calculate service amounts
        for service in services:
            total_guest_amount += service['amount']
            logger.info(f"Service assigned: {service['name']} to guest: {guest_user.username}")

        return total_guest_amount

    def assign_identification(self, booking, guest_user, rooms, identification, scenario):
        if scenario == 1:
            if not booking.identification:
                booking.identification = identification or "No ID Provided"
        elif scenario == 2:
            for room in rooms:
                if room not in booking.identification:
                    booking.identification[room] = identification or "No ID Provided"
        elif scenario == 3:
            booking.identification[guest_user.id] = identification or "No ID Provided"
        logger.info(f"Identification assigned for scenario {scenario}")