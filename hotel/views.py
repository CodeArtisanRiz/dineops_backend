import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
import json  # Import json module

from .models import Room, ServiceCategory, Service
from accounts.models import Tenant
from .serializers import RoomSerializer, ServiceCategorySerializer, ServiceSerializer
from utils.image_upload import handle_image_upload  # Import handle_image_upload

logger = logging.getLogger(__name__)

class RoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Room.objects.all()
        return Room.objects.filter(tenant=user.tenant)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = RoomSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        tenant_name = user.tenant.tenant_name if not user.is_superuser else None

        if user.is_superuser:
            tenant_id = request.data.get('tenant')
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name

        # Handle image file upload
        image_urls = handle_image_upload(request, tenant_name, 'room', 'image')
        if image_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["image"]}')
        else:
            logger.debug('No image URLs returned from handle_image_upload.')

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tenant=user.tenant if not user.is_superuser else tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        tenant_name = user.tenant.tenant_name if not user.is_superuser else room.tenant.tenant_name

        # Handle image file upload
        image_urls = handle_image_upload(request, tenant_name, 'room', 'image')
        if image_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["image"]}')
        else:
            logger.debug('No image URLs returned from handle_image_upload.')

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            tenant_id = request.data.get('tenant')
            if tenant_id:
                tenant = get_object_or_404(Tenant, id=tenant_id)
                serializer.save(tenant=tenant)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        room_number = room.room_number
        room.delete()
        return Response({"message": f"Room - {room_number} deleted"}, status=status.HTTP_204_NO_CONTENT)

class ServiceCategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = ServiceCategory.objects.all()
        serializer = ServiceCategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category)
        return Response(serializer.data)

    def create(self, request):
        serializer = ServiceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        service_category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Service.objects.all()
        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def create(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


