# from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import Tenant
from .serializers import UserSerializer, TenantSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.
UserModel = get_user_model()

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(tenant=user.tenant)
