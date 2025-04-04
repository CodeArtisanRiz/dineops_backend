
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, TenantViewSet, CustomerRegistrationView, CustomerVerificationView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tenants', TenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('customer/register/', CustomerRegistrationView.as_view(), name='customer-register'),
    path('customer/verify/', CustomerVerificationView.as_view(), name='customer-verify'),
]
