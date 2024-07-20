# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .models import FoodItem
# from .serializers import FoodItemSerializer
# # from django.shortcuts import get_object_or_404

# class FoodItemViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         queryset = FoodItem.objects.filter(tenant=request.user.tenant)
#         serializer = FoodItemSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = FoodItem.objects.filter(tenant=request.user.tenant)
#         food_item = queryset.filter(pk=pk).first()
#         if food_item is not None:
#             serializer = FoodItemSerializer(food_item)
#             return Response(serializer.data)
#         else:
#             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#     def create(self, request):
#         serializer = FoodItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(tenant=request.user.tenant)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# foods/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import FoodItem
from .serializers import FoodItemSerializer
from django.shortcuts import get_object_or_404

class FoodItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        category = request.query_params.get('category', None)
        if category:
            queryset = FoodItem.objects.filter(tenant=request.user.tenant, category=category)
        else:
            queryset = FoodItem.objects.filter(tenant=request.user.tenant)
        serializer = FoodItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = FoodItem.objects.filter(tenant=request.user.tenant)
        food_item = queryset.filter(pk=pk).first()
        if food_item is not None:
            serializer = FoodItemSerializer(food_item)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = FoodItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tenant=request.user.tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = FoodItem.objects.filter(tenant=request.user.tenant)
        food_item = get_object_or_404(queryset, pk=pk)
        serializer = FoodItemSerializer(food_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = FoodItem.objects.filter(tenant=request.user.tenant)
        food_item = get_object_or_404(queryset, pk=pk)
        food_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
