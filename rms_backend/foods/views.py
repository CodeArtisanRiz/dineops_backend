# # from django.shortcuts import render
# # from rest_framework import viewsets
# # from rest_framework.permissions import IsAuthenticated
# # from .models import FoodItem
# # from .serializers import FoodItemSerializer


# # # Create your views here.
# # class FoodItemViewSet(viewsets.ModelViewSet):
# #     queryset = FoodItem.objects.all()
# #     serializer_class = FoodItemSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         # Filter queryset to only include food items of the current tenant
# #         return self.queryset.filter(tenant=self.request.user.tenant)

# #     def perform_create(self, serializer):
# #         # Automatically set the tenant of the food item to the current user's tenant
# #         serializer.save(tenant=self.request.user.tenant)
# # foods/views.py

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .models import FoodItem
# from .serializers import FoodItemSerializer
# from django.shortcuts import get_object_or_404

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

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .models import FoodItem
# from .serializers import FoodItemSerializer
# from django.shortcuts import get_object_or_404

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
