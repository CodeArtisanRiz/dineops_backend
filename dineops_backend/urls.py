"""
URL configuration for dineops_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="DineOps",
        default_version='v1',
        description=(
            "API documentation for DineOps backend. Authentication using JWT Bearer Token.\n\n"
            "### Authentication\n"
            "To authenticate, obtain a JWT token by sending a POST request to `/api/token/` with your username and password.\n"
            "Use the returned token to authorize your requests by clicking the 'Authorize' button in the Swagger UI.\n"
            "Enter the token in the format: `Bearer {your_token}`.\n\n"
            "Example:\n"
            "```\n"
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4NTUxMTI4LCJpYXQiOjE3Mjg1NDc1MjgsImp0aSI6ImViMTU2NzdjZjY5NjQxZTk4Zjg0NTliODZlNWFjNDFhIiwidXNlcl9pZCI6M30.jVNcmlyYYetx9XUuoshlGCE2lPJolI759BO2UwHqnp0\n"
            "```\n"
        ),
        terms_of_service="https://techno3gamma.in/privacy_policy.htm",
        contact=openapi.Contact(email="connect@techno3gamma.in"),
        license=openapi.License(name="GNU General Public License v3.0"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # Include accounts app URLs
    path('api/foods/', include('foods.urls')),  # Include foods app URLs
    path('api/orders/', include('order.urls')),  # Include order app URLs
    path('api/hotel/', include('hotel.urls')),  # Include hotel app URLs
    path('api/billing/', include('billing.urls')),  # Include billing app URLs
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
