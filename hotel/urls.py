from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, CreateUserView, BookingViewSet, ServiceCategoryViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'service-categories', ServiceCategoryViewSet)
router.register(r'services', ServiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/add-service/', BookingViewSet.as_view({'post': 'add_service'}), name='add-service-to-room'),
]
