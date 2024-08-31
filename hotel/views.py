from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Room
from .serializers import RoomSerializer
from accounts.models import Tenant  # Assuming Tenant model is in accounts app


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
                raise PermissionDenied("Superuser must include tenant ID in request.")
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

        # Ensure the user has permission to delete
        if not user.is_superuser and instance.tenant != user.tenant:
            raise PermissionDenied("You do not have permission to delete this room.")

        room_number = instance.room_number  # Capture the room number before deletion
        self.perform_destroy(instance)
        
        # Return a custom response
        return Response({"message": f"Room - {room_number} deleted"}, status=status.HTTP_204_NO_CONTENT)