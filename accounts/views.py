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

        # Set default GST rates if not provided
        request.data._mutable = True
        
        # Restaurant GST defaults
        if 'restaurant_cgst' not in request.data:
            request.data['restaurant_cgst'] = '2.50'
            request.data['restaurant_sgst'] = '2.50'

        # Hotel GST defaults (if hotel feature is enabled)
        if request.data.get('has_hotel_feature'):
            if 'hotel_cgst_lower' not in request.data:
                request.data['hotel_cgst_lower'] = '6.00'
                request.data['hotel_sgst_lower'] = '6.00'
                request.data['hotel_cgst_upper'] = '9.00'
                request.data['hotel_sgst_upper'] = '9.00'
                request.data['hotel_gst_limit_margin'] = '7500.00'

            # Service GST defaults
            if 'service_cgst_lower' not in request.data:
                request.data['service_cgst_lower'] = '9.00'
                request.data['service_sgst_lower'] = '9.00'
                request.data['service_cgst_upper'] = '14.00'
                request.data['service_sgst_upper'] = '14.00'
                # service_gst_limit_margin is optional, so not setting a default

        request.data._mutable = False

        # Handle logo upload and other operations
        logo_urls = handle_image_upload(request, request.data.get('tenant_name'), 'logo', 'logo')
        if logo_urls:
            request.data._mutable = True
            request.data['logo'] = json.dumps(logo_urls)
            request.data._mutable = False

        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            tenant = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        tenant = self.get_object()

        if not user.is_superuser and tenant.id != user.tenant_id:
            raise PermissionDenied("You do not have permission to perform this action.")

        # Check if GST rates are being updated by a non-superuser
        gst_fields = [
            'restaurant_cgst', 'restaurant_sgst',
            'hotel_cgst_lower', 'hotel_sgst_lower',
            'hotel_cgst_upper', 'hotel_sgst_upper',
            'hotel_gst_limit_margin',
            'service_cgst_lower', 'service_sgst_lower',
            'service_cgst_upper', 'service_sgst_upper',
            'service_gst_limit_margin'
        ]
        
        if not user.is_superuser:
            for field in gst_fields:
                if field in request.data:
                    raise PermissionDenied(
                        "Only superusers can update GST rates and margins."
                    )

        # Handle logo upload and continue with update
        logo_urls = handle_image_upload(request, tenant.tenant_name, 'logo', 'logo')
        if logo_urls:
            request.data._mutable = True
            request.data['logo'] = json.dumps(logo_urls)
            request.data._mutable = False

        # Track modifications
        tenant.modified_at.append(datetime.now(timezone.utc).isoformat())
        tenant.modified_by.append(f"{user.username}({user.id})")
        tenant.save()

        return super().update(request, *args, **kwargs)

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

