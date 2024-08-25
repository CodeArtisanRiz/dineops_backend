from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Room, Reservation, RoomHistory
from .serializers import RoomSerializer, ReservationSerializer, RoomHistorySerializer
from accounts.permissions import IsSuperuser

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Room.objects.all()
        if user.tenant:
            return Room.objects.filter(tenant=user.tenant)
        return Room.objects.none()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Reservation.objects.select_related('room', 'guest').all()
        return Reservation.objects.select_related('room', 'guest').filter(tenant=user.tenant)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        reservation = self.get_object()
        room = reservation.room
        room.status = 'occupied'
        room.save()
        return Response({'message': 'Check-in successful'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        reservation = self.get_object()
        room = reservation.room
        room.status = 'available'
        room.save()
        return Response({'message': 'Check-out successful'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def switch_room(self, request, pk=None):
        reservation = self.get_object()
        new_room_id = request.data.get('new_room_id')

        if not new_room_id or str(reservation.room.id) == str(new_room_id):
            return Response({'error': 'New room ID is required and should be different from current room'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            new_room = Room.objects.get(id=new_room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Invalid room ID'}, status=status.HTTP_400_BAD_REQUEST)

        old_room = reservation.room
        old_room.status = 'available'
        old_room.save()

        new_room.status = 'occupied'
        new_room.save()

        reservation.room = new_room
        reservation.save()

        RoomHistory.objects.create(
            reservation=reservation,
            room=old_room,
            start_date=reservation.check_in,
            end_date=timezone.now()
        )

        return Response({'message': 'Room switch successful'}, status=status.HTTP_200_OK)

class RoomHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoomHistory.objects.all()
    serializer_class = RoomHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RoomHistory.objects.all()
        return RoomHistory.objects.filter(reservation__tenant=user.tenant)