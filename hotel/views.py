from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Room
from .serializers import RoomSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSuperuser
from rest_framework.exceptions import ValidationError
import logging



logger = logging.getLogger(__name__)

class RoomViewSet(viewsets.ViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)
        
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)
        

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        room_number = instance.room_number
        self.perform_destroy(instance)
        return Response({"room_number": room_number, "message": "deleted"}, status=status.HTTP_204_NO_CONTENT)
