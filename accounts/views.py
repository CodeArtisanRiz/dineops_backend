from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Tenant
from .serializers import UserSerializer, TenantSerializer, TableSerializer
from utils.permissions import IsSuperuser, IsTenantAdmin
import requests
import json  # Import json module
import logging
from utils.image_upload import handle_image_upload
from datetime import timezone, datetime  # Import datetime module

logger = logging.getLogger(__name__)

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        elif user.role in ['admin', 'manager']:
            return Tenant.objects.filter(id=user.tenant_id)
        return Tenant.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsSuperuser | IsTenantAdmin]
        else:
            permission_classes = [IsSuperuser]
        return [permission() for permission in permission_classes]

    def create(self, request):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        tenant_name = request.data.get('tenant_name')
        if not tenant_name:
            return Response({'error': 'Tenant name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        logo_urls = handle_image_upload(request, tenant_name, 'logo', 'logo')
        if logo_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['logo'] = json.dumps(logo_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["logo"]}')

        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            tenant = serializer.save()
            total_tables = int(request.data.get('total_tables', 0))  # Convert to int here
            return Response(serializer.data, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        tenant = self.get_object()

        if not user.is_superuser and tenant.id != user.tenant_id:
            raise PermissionDenied("You do not have permission to perform this action.")

        # Check if subscription fields are being updated by a non-superuser
        if not user.is_superuser:
            if 'subscription_from' in request.data or 'subscription_to' in request.data:
                raise PermissionDenied("Only superusers can update subscription fields.")

        total_tables = request.data.get('total_tables', None)

        logo_urls = handle_image_upload(request, tenant.tenant_name, 'logo', 'logo')
        if logo_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['logo'] = json.dumps(logo_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["logo"]}')
        
        # Append to modified_at and modified_by fields
        tenant.modified_at.append(datetime.now(timezone.utc).isoformat())
        tenant.modified_by.append(f"{user.username}({user.id})")
        tenant.save()

        response = super().update(request, *args, **kwargs)
        if total_tables is not None:
            total_tables = int(total_tables)
            current_count = tenant.tables.count()
            if total_tables > current_count:
                self.create_tables(tenant, total_tables - current_count)
            elif total_tables < current_count:
                self.remove_tables(tenant, current_count - total_tables)
            tenant.total_tables = total_tables  # Ensure tenant.total_tables is updated
        return response

    def remove_tables(self, tenant, count):
        tables_to_delete = tenant.tables.all().order_by('-table_number')[:count]
        for table in tables_to_delete:
            table.delete()

UserModel = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            tenant_id = self.request.query_params.get('tenant_id')
            if tenant_id:
                return self.queryset.filter(tenant_id=tenant_id)
            return self.queryset
        return self.queryset.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        user = self.request.user
        role = self.request.data.get('role')

        if role == 'admin' and not user.is_superuser:
            raise PermissionDenied("Only superusers can create admin users.")

        if user.is_superuser:
            tenant_id = self.request.data.get('tenant')
            if tenant_id:
                serializer.save(tenant_id=tenant_id)
            else:
                raise PermissionDenied("Superuser must include tenant ID in request.")
        else:
            serializer.save(tenant=user.tenant)

    def perform_update(self, serializer):
        user = self.request.user
        role = self.request.data.get('role')

        if role == 'admin' and not user.is_superuser:
            raise PermissionDenied("Only superusers can update to admin role.")

        if user.is_superuser:
            tenant_id = self.request.data.get('tenant')
            if tenant_id:
                serializer.save(tenant_id=tenant_id)
            else:
                raise PermissionDenied("Superuser must include tenant ID in request.")
        else:
            serializer.save()

