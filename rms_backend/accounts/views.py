
# Import necessary modules
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import Tenant
from .serializers import UserSerializer, TenantSerializer
from rest_framework.permissions import IsAuthenticated



# Get the User model
UserModel = get_user_model()

# ViewSet for Tenant model
class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

# ViewSet for User model
class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current user
        user = self.request.user
        # Filter queryset to only include users from the same tenant
        return self.queryset.filter(tenant=user.tenant)
