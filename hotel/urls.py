from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, CreateUserView, BookingViewSet  # Import the new view

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)  # Add the booking route

urlpatterns = [
    path('', include(router.urls)),
]
