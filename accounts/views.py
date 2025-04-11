# Remove duplicate imports and organize them
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import requests
import json
import logging
import random
import string
from .models import Tenant, PhoneVerification
from .serializers import UserSerializer, TenantSerializer, TableSerializer, PhoneVerificationSerializer
from utils.permissions import IsSuperuser, IsTenantAdmin, IsManager
from utils.image_upload import handle_image_upload
from utils.otp_auth import generate_verification_data, verify_otp
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import random
import string

logger = logging.getLogger(__name__)

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Tenant.objects.all()
        elif user.role in ['admin', 'manager']:
            queryset = Tenant.objects.filter(id=user.tenant_id)
        else:
            queryset = Tenant.objects.none()
        
        logger.debug(f"User: {user.username}, Role: {user.role}, Queryset: {queryset}")
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsSuperuser | IsTenantAdmin | IsManager]
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

        # Track modifications using Django's timezone
        tenant.modified_at.append(timezone.now().isoformat())
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
        elif user.role in ['admin', 'manager']:
            # Allow admin and managers to see all users (including customers) of their tenant
            return self.queryset.filter(tenant=user.tenant)
        else:
            # Allow users to see their own profile
            return self.queryset.filter(id=user.id)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = UserModel.objects.get(id=kwargs.get('pk'))
            # Check permissions
            if not request.user.is_superuser:
                # Admin/Manager can view any user in their tenant
                if request.user.role in ['admin', 'manager']:
                    if request.user.tenant != instance.tenant:
                        raise PermissionDenied("You do not have permission to view users from other tenants.")
                # Regular users can only view their own profile
                elif request.user.id != instance.id:
                    raise PermissionDenied("You can only view your own profile.")
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

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



class CustomerRegistrationView(APIView):
    permission_classes = []

    def generate_temp_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def post(self, request):
        tenant_id = request.data.get('tenant_id')
        method = request.data.get('method', 'phone')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        
        if not tenant_id:
            return Response({
                'error': 'tenant_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for existing users with either email or phone
        if email and UserModel.objects.filter(email=email).exists():
            return Response({
                'error': 'Email is already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if phone and UserModel.objects.filter(phone=phone).exists():
            return Response({
                'error': 'Phone number is already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if method not in ['phone', 'email']:
            return Response({
                'error': 'Invalid verification method. Use "phone" or "email"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate based on method
        if method == 'email':
            email = request.data.get('email')
            if not email:
                return Response({
                    'error': 'email is required for email verification'
                }, status=status.HTTP_400_BAD_REQUEST)
            username = f"customer_{email}"
            identifier = email
        else:
            phone = request.data.get('phone')
            if not phone:
                return Response({
                    'error': 'phone is required for phone verification'
                }, status=status.HTTP_400_BAD_REQUEST)
            username = f"customer_{phone}"
            identifier = phone
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({
                'error': 'Invalid tenant_id'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if UserModel.objects.filter(username=username).exists():
            return Response({
                'error': f'User with this {method} already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP and token based on method
        otp, token = generate_verification_data(method)
        verification_token = f"{otp}{token}"
        
        temp_password = self.generate_temp_password()
        user_data = {
            'username': username,
            'password': temp_password,
            'phone': request.data.get('phone', ''),
            'email': request.data.get('email', ''),
            'tenant': tenant.id,
            'role': 'customer',
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'address_line_1': request.data.get('address_line_1', ''),
            'address_line_2': request.data.get('address_line_2', ''),
            'city': request.data.get('city', ''),
            'state': request.data.get('state', ''),
            'country': request.data.get('country', ''),
            'pin': request.data.get('pin', ''),
            'dob': request.data.get('dob'),
            'is_verified': False,
        }

        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save(tenant=tenant)
            
            # Store verification details based on method
            PhoneVerification.objects.create(
                phone=identifier,  # Use identifier instead of phone
                verification_id=verification_token,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            return Response({
                'message': f'Verification code sent to your {method}',
                'identifier': identifier,  # Return the identifier used
                'user_id': user.id,
                'verification_id': token  # Send only token part
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        verification_id = request.data.get('verification_id')

        if not all([phone, code, verification_id]):
            return Response({
                'error': 'phone, code and verification_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = PhoneVerification.objects.get(
                phone=phone,
                verification_id__endswith=verification_id,  # Match token part
                expires_at__gt=timezone.now(),
                is_verified=False
            )
            
            is_valid, message = verify_otp(verification, code)
            
            if is_valid:
                # Update user verification status
                user = UserModel.objects.get(phone=phone)
                user.is_verified = True
                user.save()
                
                # Mark verification as complete
                verification.is_verified = True
                verification.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            # Failed verification attempt
            verification.attempts += 1
            verification.save()
            
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except PhoneVerification.DoesNotExist:
            return Response({
                'error': 'Invalid or expired verification session'
            }, status=status.HTTP_400_BAD_REQUEST)

