# hotel/views.py

# from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
# from .models import Room
# from .serializers import RoomSerializer
from accounts.permissions import IsSuperuser

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            tenant = self.request.data.get('tenant')
            if not tenant:
                raise ValidationError({'tenant': 'Tenant is required for superuser'})
            serializer.save(tenant_id=tenant)
        else:
            serializer.save(tenant=self.request.user.tenant)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Room.objects.all()
        return Room.objects.filter(tenant=self.request.user.tenant)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        reservation = self.get_object()
        check_in_time = request.data.get('check_in_time', timezone.now())
        reservation.status = 'checked_in'
        reservation.actual_check_in = check_in_time
        reservation.save()
        return Response({'status': 'checked in', 'check_in_time': reservation.actual_check_in})

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        reservation = self.get_object()
        check_out_time = request.data.get('check_out_time', timezone.now())
        reservation.status = 'checked_out'
        reservation.actual_check_out = check_out_time
        reservation.save()
        reservation.room.is_available = True
        reservation.room.save()
        return Response({'status': 'checked out', 'check_out_time': reservation.actual_check_out})
