import logging
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room
from .models import Booking
from accounts.models import Tenant, User
from .serializers import RoomSerializer, BookingSerializer, BaseGuestSerializer
from rest_framework import status
from accounts.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
import logging

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


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = BaseGuestSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return response
        except Exception as e:
            logger.error("Error retrieving bookings: %s", e)
            return Response({"detail": "An error occurred while retrieving bookings.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except Exception as e:
                logger.error("Error creating booking: %s", e)
                return Response({"detail": "An error occurred while creating the booking.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error("Error updating booking: %s", e)
                return Response({"detail": "An error occurred while updating the booking.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            # Set associated rooms to available
            rooms = instance.rooms.all()
            for room in rooms:
                room.status = 'available'
                room.booking_id = None
                room.save()

            self.perform_destroy(instance)
            return Response({"booking_id": instance.id, "detail": "deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Error deleting booking: %s", e)
            return Response({"detail": "An error occurred while deleting the booking.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


