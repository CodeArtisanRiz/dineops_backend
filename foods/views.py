from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import logging
import json  # Import json module
from foods.models import Table
from foods.serializers import TableSerializer


from .models import FoodItem, Category, Tenant
from .serializers import FoodItemSerializer, CategorySerializer
from utils.image_upload import handle_image_upload

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
            category_id = request.data.get('category')  # Change from 'category_id' to 'category'
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name

            # Handle image file upload
            image_urls = handle_image_upload(request, tenant_name, 'food_category', 'image')
            if image_urls:
                request.data._mutable = True  # Make request data mutable
                request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Image URLs added to request data: {request.data["image"]}')

            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'manager']:
            tenant_name = user.tenant.tenant_name
            # Handle image file upload
            image_urls = handle_image_upload(request, tenant_name, 'food_category', 'image')
            if image_urls:
                request.data._mutable = True  # Make request data mutable
                request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Image URLs added to request data: {request.data["image"]}')

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
        image_urls = handle_image_upload(request, tenant_name, 'food_category', 'image')
        if image_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["image"]}')

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            modified_by_list = category.modified_by
            modified_by_list.append(user.username)
            serializer.save(modified_by=modified_by_list)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role not in ['admin', 'manager']:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        category = get_object_or_404(queryset, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role != 'manager':
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        category = get_object_or_404(queryset, pk=pk)
        category.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({f'message : Category {category} deleted.'}, status=status.HTTP_204_NO_CONTENT)


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
            category_id = request.data.get('category')  # Change from 'category_id' to 'category'
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name
            category = get_object_or_404(Category, id=category_id, tenant=tenant)

            # Handle image file upload
            image_urls = handle_image_upload(request, tenant_name, 'food_item', 'image')
            if image_urls:
                request.data._mutable = True  # Make request data mutable
                request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Image URLs added to request data: {request.data["image"]}')

            serializer = FoodItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user, tenant=tenant, category=category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'manager']:
            tenant_name = user.tenant.tenant_name
            category_id = request.data.get('category')  # Change from 'category_id' to 'category'
            category = get_object_or_404(Category, id=category_id, tenant=user.tenant)
            
            # Handle image file upload
            image_urls = handle_image_upload(request, tenant_name, 'food_item', 'image')
            if image_urls:
                request.data._mutable = True  # Make request data mutable
                request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Image URLs added to request data: {request.data["image"]}')

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
        image_urls = handle_image_upload(request, tenant_name, 'food_item', 'image')
        if image_urls:
            # Convert request.data to a mutable dictionary
            data = request.data.copy()  # Create a mutable copy
            data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            logger.debug(f'Image URLs added to request data: {data["image"]}')
        else:
            data = request.data  # Use original data if no images

        # Handle category update
        category_id = data.get('category')  # Change from 'category_name' to 'category'
        if category_id:
            category = get_object_or_404(Category, id=category_id, tenant=user.tenant)
            data['category'] = category.id  # Ensure category ID is set

        serializer = FoodItemSerializer(food_item, data=data, partial=True)
        if serializer.is_valid():
            modified_by_list = food_item.modified_by
            modified_by_list.append(user.username)
            serializer.save(modified_by=modified_by_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)  # Reuse the update logic

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser and user.role not in ['admin', 'manager']:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        food_item = get_object_or_404(queryset, pk=pk)
        food_item_id = food_item.id  # Store the ID of the food item to be deleted
        food_item.delete()  # Delete the food item

        # Return a response indicating the ID of the deleted food item
        return Response({f'message : Food item {food_item_id} deleted.'}, status=status.HTTP_204_NO_CONTENT)

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Table.objects.all()
        return Table.objects.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        if serializer.is_valid():
            # Get the tenant from the validated data
            tenant = serializer.validated_data.get('tenant')
            if not tenant:
                # Raise PermissionDenied if no tenant is assigned
                raise PermissionDenied("Table must be assigned to a tenant.")

            # Calculate the new table number
            table_number = tenant.tables.count() + 1  # Set the table number correctly
            # Save the serializer with the new table number
            serializer.save(table_number=table_number)

            # Increment the total tables count for the tenant
            tenant.total_tables += 1
            # Save the updated tenant
            tenant.save()
        else:
            raise ValidationError(serializer.errors)

        # serializer.save()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # No additional action required on tenant

    def perform_destroy(self, instance):
        tenant = instance.tenant
        instance.delete()

        tenant.total_tables -= 1
        tenant.save()
        
        # Return a response message for deletion with status 200
        # Return a response indicating the ID of the deleted food item
        return Response({f'message : Table {Table} deleted.'}, status=status.HTTP_204_NO_CONTENT)

