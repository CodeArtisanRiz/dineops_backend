from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Tenant
from .serializers import UserSerializer, TenantSerializer
from .permissions import IsSuperuser
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import logging



# class TenantViewSet(viewsets.ModelViewSet):
#     queryset = Tenant.objects.all()
#     serializer_class = TenantSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser:
#             return Tenant.objects.all()
#         elif user.role in ['admin', 'manager']:
#             return Tenant.objects.filter(id=user.tenant_id)
#         return Tenant.objects.none()

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [IsAuthenticated]
#         else:
#             permission_classes = [IsSuperuser]
#         return [permission() for permission in permission_classes]

logger = logging.getLogger(__name__)
class TenantViewSet(viewsets.ModelViewSet):
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

        self.handle_image_upload(request, tenant_name)

        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_image_upload(self, request, tenant_name):
        image_file = request.FILES.get('logo')
        if image_file:
            image_url = self.upload_image(image_file, tenant_name)
            if image_url:
                validate = URLValidator()
                try:
                    validate(image_url)
                    request.data._mutable = True
                    request.data['logo_url'] = image_url
                    request.data._mutable = False
                    logger.debug(f'Successfully added image URL to request data: {request.data["logo_url"]}')
                except ValidationError as e:
                    logger.error(f'Invalid image URL: {image_url}, Error: {e}')
                    raise PermissionDenied('Failed to upload image: Invalid URL.')
            else:
                raise PermissionDenied('Failed to upload image.')

    def upload_image(self, image_file, tenant_name):
        files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
        data = {'tenant': tenant_name}
        response = requests.post('https://techno3gamma.in/bucket/dineops/handle_tenant_logo.php', files=files, data=data)

        if response.status_code == 200:
            data = response.json()
            image_url = data.get('image_url')
            logger.debug(f'Uploaded image URL: {image_url}')
            return image_url
        return None

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