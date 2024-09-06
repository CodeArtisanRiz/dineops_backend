import logging
from rest_framework import viewsets, status, generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room, Booking, ServiceCategory, Service
from accounts.models import Tenant, User
from .serializers import RoomSerializer, BookingSerializer, BaseGuestSerializer, ServiceCategorySerializer, ServiceSerializer, AddServiceToRoomSerializer, RoomDetailUpdateSerializer, RoomCheckOutSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import APIView

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error("An error occurred while creating the booking: %s", e)
            return Response({"detail": "An error occurred while creating the booking.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def checkin(self, request, pk=None):
        booking = self.get_object()
        room_number = request.data.get('room_number')
        check_in = request.data.get('check_in')

        for room_detail in booking.room_details:
            if room_detail['room_number'] == room_number:
                room_detail['check_in'] = check_in
                break

        booking.save()
        return Response({"detail": "Check-in successful."}, status=status.HTTP_200_OK)

    def checkout(self, request, pk=None):
        booking = self.get_object()
        room_number = request.data.get('room_number')
        check_out = request.data.get('check_out')
        total_amount = request.data.get('total_amount')
        discount = request.data.get('discount')
        net_amount = request.data.get('net_amount')

        for room_detail in booking.room_details:
            if room_detail['room_number'] == room_number:
                room_detail['check_out'] = check_out
                room_detail['total_amount'] = total_amount
                room_detail['discount'] = discount
                room_detail['net_amount'] = net_amount
                break

        booking.save()
        return Response({"detail": "Check-out successful."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='add-service')
    def add_service(self, request):
        serializer = AddServiceToRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

class UpdateRoomCheckInView(APIView):
    def patch(self, request, booking_id, room_id):
        serializer = RoomDetailUpdateSerializer(data=request.data)
        if serializer.is_valid():
            room_number = serializer.validated_data['room_number']
            check_in = serializer.validated_data.get('check_in')
            check_out = serializer.validated_data.get('check_out')

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

            room_found = False
            for room_detail in booking.room_details:
                if room_detail['room_number'] == room_number:
                    if check_in:
                        room_detail['check_in'] = check_in.isoformat()
                    if check_out:
                        room_detail['check_out'] = check_out.isoformat()
                        # Reset room status and remove booking period
                        try:
                            room = Room.objects.get(id=room_id)
                            room.status = 'available'
                            room.booked_periods = [period for period in room.booked_periods if period['booking_id'] != booking_id]
                            room.save()
                        except Room.DoesNotExist:
                            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
                    room_found = True
                    break

            if not room_found:
                return Response({"detail": "Room not found in booking."}, status=status.HTTP_404_NOT_FOUND)

            booking.save()
            return Response({"detail": "Room details updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateRoomCheckOutView(APIView):
    def patch(self, request, booking_id, room_id):
        serializer = RoomCheckOutSerializer(data=request.data)
        if serializer.is_valid():
            room_number = serializer.validated_data['room_number']
            check_out = serializer.validated_data['check_out']

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

            room_found = False
            for room_detail in booking.room_details:
                if room_detail['room_number'] == room_number:
                    room_detail['check_out'] = check_out.isoformat()
                    # Reset room status and remove booking period
                    try:
                        room = Room.objects.get(id=room_id)
                        room.status = 'available'
                        room.booked_periods = [period for period in room.booked_periods if period['booking_id'] != booking_id]
                        room.save()
                    except Room.DoesNotExist:
                        return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
                    room_found = True
                    break

            if not room_found:
                return Response({"detail": "Room not found in booking."}, status=status.HTTP_404_NOT_FOUND)

            booking.save()
            return Response({"detail": "Check-out time updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


