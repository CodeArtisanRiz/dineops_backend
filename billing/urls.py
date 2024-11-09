from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BillViewSet, BillPaymentViewSet

router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bill')
router.register(r'bill-payments', BillPaymentViewSet, basename='bill-payment')

urlpatterns = [
    path('', include(router.urls)),
]
