from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import logging

from .models import FoodItem, Category, Tenant
from .serializers import FoodItemSerializer, CategorySerializer
from .utils import handle_image_upload  # Import the utility function

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Category.objects.all()
        return Category.objects.filter(tenant=user.tenant)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        category = get_object_or_404(queryset, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        if user.is_superuser:
            tenant_id = request.data.get('tenant')
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name

            # Handle image file upload
            handle_image_upload(request, tenant_name)

            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'manager']:
            tenant_name = user.tenant.tenant_name
            # Handle image file upload
            handle_image_upload(request, tenant_name)
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=user.tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied("You do not have permission to perform this action.")

    def update(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role not in ['admin', 'manager']:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        category = get_object_or_404(queryset, pk=pk)
        tenant_name = user.tenant.tenant_name if not user.is_superuser else category.tenant.tenant_name

        # Handle image file upload
        handle_image_upload(request, tenant_name)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            modified_by_list = category.modified_by
            modified_by_list.append(user.username)
            serializer.save(modified_by=modified_by_list)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role != 'manager':
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        category = get_object_or_404(queryset, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

            
class FoodItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return FoodItem.objects.all()
        return FoodItem.objects.filter(tenant=user.tenant)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = FoodItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        food_item = get_object_or_404(queryset, pk=pk)
        serializer = FoodItemSerializer(food_item)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        if user.is_superuser:
            tenant_id = request.data.get('tenant')
            category = request.data.get('category')
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name
            category = get_object_or_404(Category, id=category_id, tenant=tenant)

            # Handle image file upload
            handle_image_upload(request, tenant_name)

            serializer = FoodItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=tenant, category=category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'manager']:
            tenant_name = user.tenant.tenant_name
            category_id = request.data.get('category_id')
            category = get_object_or_404(Category, id=category_id, tenant=user.tenant)
            
            # Handle image file upload
            handle_image_upload(request, tenant_name)
            serializer = FoodItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=user.tenant, category=category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied("You do not have permission to perform this action.")

    def update(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role not in ['admin', 'manager']:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        food_item = get_object_or_404(queryset, pk=pk)
        tenant_name = user.tenant.tenant_name if not user.is_superuser else food_item.tenant.tenant_name

        # Handle image file upload
        handle_image_upload(request, tenant_name)

        # Handle category update
        category_id = request.data.get('category_id')
        if category_id:
            category = get_object_or_404(Category, id=category_id, tenant=user.tenant)
            # request.data._mutable = True
            request.data['category'] = category.id
            # request.data._mutable = False

        serializer = FoodItemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            modified_by_list = food_item.modified_by
            modified_by_list.append(user.username)
            serializer.save(modified_by=modified_by_list)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role != 'manager':
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        food_item = get_object_or_404(queryset, pk=pk)
        food_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
