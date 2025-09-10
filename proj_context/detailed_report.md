# dineops_backend Project Context

Generated on: Wed Sep 10 15:14:09 IST 2025

## Project Overview

dineops_backend is a comprehensive Django-based backend system for managing restaurant and hotel operations, including user management, food ordering, room bookings, and billing.

## Project Structure

### Main Directories

  - order
  - cache
  - hotel
  - utils
  - staticfiles
  - accounts
  - scripts
  - templates
  - dineops_backend
  - foods
  - billing
  - proj_context

### App Structure

#### accounts/
accounts/models.py
accounts/serializers.py
accounts/__init__.py
accounts/apps.py
accounts/admin.py
accounts/tests.py
accounts/urls.py
accounts/views.py

#### billing/
billing/services.py
billing/models.py
billing/serializers.py
billing/__init__.py
billing/apps.py
billing/admin.py
billing/tests.py
billing/urls.py
billing/views.py

#### foods/
foods/signals.py
foods/models.py
foods/serializers.py
foods/__init__.py
foods/apps.py
foods/admin.py
foods/tests.py
foods/urls.py
foods/views.py

#### hotel/
hotel/models.py
hotel/serializers.py
hotel/__init__.py
hotel/apps.py
hotel/admin.py
hotel/tests.py
hotel/urls.py
hotel/views.py

#### order/
order/models.py
order/serializers.py
order/__init__.py
order/apps.py
order/admin.py
order/tests.py
order/urls.py
order/views.py


## Key Files Content

### Settings (dineops_backend/settings.py)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django REST Framework for building APIs
    'rest_framework',
    # Simple JWT for token-based authentication
...
```

### Main URLs (dineops_backend/urls.py)

```python
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    path('', views.home, name='home'),
    path('root-files/', views.list_root_files, name='list_root_files'),
    path('db/', views.download_db, name='download_database'),
    path('api/backup/', views.download_db_page, name='download_db_page'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # Include accounts app URLs
    path('api/foods/', include('foods.urls')),  # Include foods app URLs
...
```

### accounts app

#### Models (accounts/models.py)

```python
class Tenant
class PhoneVerification
```

#### Views (accounts/views.py)

```python
class TenantViewSet
class UserViewSet
```

#### URLs (accounts/urls.py)

```python

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TenantViewSet, CustomerRegistrationView, CustomerVerificationView, TokenObtainPairViewWithTag, TokenRefreshViewWithTag

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tenants', TenantViewSet)

urlpatterns = [
...
```


### billing app

#### Models (billing/models.py)

```python
class Bill
class BillPayment
```

#### Views (billing/views.py)

```python
class BillViewSet
class BillPaymentViewSet
```

#### URLs (billing/urls.py)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BillViewSet, BillPaymentViewSet

router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bill')
router.register(r'bill-payments', BillPaymentViewSet, basename='bill-payment')

urlpatterns = [
    path('', include(router.urls)),
...
```


### foods app

#### Models (foods/models.py)

```python
class Category
class FoodItem
class Table
```

#### Views (foods/views.py)

```python
class CategoryViewSet
class FoodItemViewSet
class TableViewSet
```

#### URLs (foods/urls.py)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodItemViewSet, CategoryViewSet, TableViewSet

app_name = 'foods'

router = DefaultRouter()
router.register(r'fooditems', FoodItemViewSet, basename='fooditem')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tables', TableViewSet)
...
```


### hotel app

#### Models (hotel/models.py)

```python
class Room
class ServiceCategory
class Service
class Booking
class RoomBooking
class CheckIn
class CheckOut
class ServiceUsage
class GuestDetails
```

#### Views (hotel/views.py)

```python
class RoomViewSet
class ServiceCategoryViewSet
class ServiceViewSet
class BookingViewSet
class RoomBookingViewSet
class CheckInViewSet
class CheckOutViewSet
class ServiceUsageViewSet
```

#### URLs (hotel/urls.py)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, ServiceCategoryViewSet, ServiceViewSet, BookingViewSet, RoomBookingViewSet, CheckInViewSet, CheckOutViewSet, ServiceUsageViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'room-bookings', RoomBookingViewSet, basename='roombooking')
...
```


### order app

#### Models (order/models.py)

```python
class Order
```

#### Views (order/views.py)

```python
class OrderViewSet
```

#### URLs (order/urls.py)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet


router = DefaultRouter()
router.register(r'order', OrderViewSet, basename='order')


urlpatterns = [
...
```


## Configuration Files

### Requirements (requirements.txt)

```
Django
djangorestframework
djangorestframework-simplejwt
# djongo
django-cors-headers
Pillow
requests
drf-yasg
setuptools
# Server
...
```

### Dockerfile

```dockerfile
# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
...
```

### Docker Compose (docker-compose.yaml)

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: dineops_backend
    env_file:
      - .env
    ports:
      - "${PORT}:${PORT}"
    volumes:
      - static_volume:/app/staticfiles
    restart: always

volumes:
...
```

## API Endpoints

### Accounts
- GET/POST /api/accounts/users/ - User management
- GET/POST /api/accounts/tenants/ - Tenant management

### Foods
- GET/POST /api/foods/categories/ - Food categories
- GET/POST /api/foods/fooditems/ - Food items

### Orders
- GET/POST /api/orders/orders/ - Order processing

### Hotel
- GET/POST /api/hotel/rooms/ - Room management
- GET/POST /api/hotel/bookings/ - Booking management
- GET/POST /api/hotel/checkin/ - Check-in operations
- GET/POST /api/hotel/checkout/ - Check-out operations

### Billing
- GET/POST /api/billing/bills/ - Billing operations
- GET/POST /api/billing/bill-payments/ - Payment processing

