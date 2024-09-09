from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, ServiceCategoryViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
