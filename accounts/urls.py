
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TenantViewSet, CustomerRegistrationView, CustomerVerificationView, TokenObtainPairViewWithTag, TokenRefreshViewWithTag

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tenants', TenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairViewWithTag.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshViewWithTag.as_view(), name='token_refresh'),
    path('users/customer/register/', CustomerRegistrationView.as_view(), name='customer-register'),
    path('users/customer/verify/', CustomerVerificationView.as_view(), name='customer-verify'),
]
