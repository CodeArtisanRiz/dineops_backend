from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, ServiceCategoryViewSet, ServiceViewSet, BookingViewSet, RoomBookingViewSet, CheckInViewSet, CheckOutViewSet, ServiceUsageViewSet, PaymentViewSet, BillingViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'room-bookings', RoomBookingViewSet, basename='roombooking')
router.register(r'checkin', CheckInViewSet, basename='checkin')
router.register(r'checkout', CheckOutViewSet, basename='checkout')
router.register(r'service-usages', ServiceUsageViewSet, basename='serviceusage')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Path for creating a billing entry
    path('billing/create/', BillingViewSet.as_view(), name='billing-create'),
    
    # Path for retrieving a specific billing entry
    path('billing/<int:billing_id>/', BillingViewSet.as_view(), name='billing-detail'),
    
    # Path for listing all billing entries
    path('billing/', BillingViewSet.as_view(), name='billing-list'),
]
