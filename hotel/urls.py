from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, ServiceCategoryViewSet, ServiceViewSet, BookingViewSet, RoomBookingViewSet, CheckInViewSet, CheckOutViewSet, ServiceUsageViewSet, PaymentViewSet, BillingView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'room-bookings', RoomBookingViewSet, basename='roombooking')
router.register(r'checkin', CheckInViewSet, basename='checkin')
router.register(r'checkout', CheckOutViewSet, basename='checkout')
router.register(r'service-usages', ServiceUsageViewSet, basename='serviceusage')
# router.register(r'billings', BillingViewSet, basename='billing')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    # path('billing/<int:booking_id>/', BillingDetailView.as_view(), name='billing-detail'),
    
    path('billing/<int:booking_id>/', BillingView.as_view(), name='billing'),
    # Path for creating a billing entry
    # path('billing/create/<int:booking_id>/', BillingView.as_view(), name='billing-create'),
    
    # Path for deleting a billing entry
    path('billing/delete/<int:billing_id>/', BillingView.as_view(), name='billing-delete'),
]
