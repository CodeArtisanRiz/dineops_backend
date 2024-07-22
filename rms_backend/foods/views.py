from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from .models import FoodItem
from .serializers import FoodItemSerializer

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
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            serializer = FoodItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant_id=tenant_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'manager']:
            serializer = FoodItemSerializer(data=request.data)
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
        food_item = get_object_or_404(queryset, pk=pk)
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