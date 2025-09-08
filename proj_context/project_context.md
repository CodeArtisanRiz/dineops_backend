# dineops_backend - Project Context

## Overview
This is a multi-tenant restaurant management system built with Django and Django REST framework for the backend. It includes user authentication, food management features, and tenant-specific data management. Future features will include hotel management, POS functionality, and real-time data updates.

## Technology Stack
- **Backend Framework**: Django 5.0.7
- **API Framework**: Django REST Framework
- **Database**: MySQL (primary) with SQLite fallback
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Deployment**: Docker + Gunicorn
- **Static Files**: WhiteNoise
- **CORS**: django-cors-headers

## Core Applications

### 1. Accounts
Handles user authentication and tenant management.

**Models**:
- `Tenant`: Manages tenant-specific information including GST rates, address, contact details
- `User`: Custom user model with role-based access control (superuser, admin, manager, staff, customer, guest)

### 2. Foods
Manages food items, categories, and restaurant tables.

**Models**:
- `Category`: Food categories with status and image support
- `FoodItem`: Individual food items with pricing, description, and category association
- `Table`: Restaurant tables with occupancy status

### 3. Order
Handles order management for the restaurant.

**Models**:
- `Order`: Customer orders with status tracking (in_progress, on_hold, kot, served, settled, cancelled)

### 4. Hotel
Provides hotel management features as an optional add-on.

**Models**:
- `Room`: Hotel rooms with type, amenities, and pricing
- `ServiceCategory`: Categories for hotel services
- `Service`: Individual hotel services
- `Booking`: Room bookings with status tracking
- `RoomBooking`: Association between bookings and rooms
- `CheckIn`/`CheckOut`: Guest check-in and check-out tracking
- `ServiceUsage`: Tracking of services used by guests
- `GuestDetails`: Additional information about hotel guests

### 5. Billing
Manages billing and payment processing for both restaurant and hotel services.

**Models**:
- `Bill`: Detailed billing information with GST breakdown
- `BillPayment`: Individual payment tracking against bills

## Authentication
The system uses JWT Bearer Token authentication.

### Endpoints
1. **Obtain Token**
   - URL: `/api/accounts/token/`
   - Method: POST
   - Description: Obtain access and refresh tokens

2. **Refresh Token**
   - URL: `/api/accounts/token/refresh/`
   - Method: POST
   - Description: Refresh access token using refresh token

## API Structure
The API is organized by application:
- `/api/accounts/` - User and tenant management
- `/api/foods/` - Food items and categories
- `/api/orders/` - Order management
- `/api/hotel/` - Hotel management
- `/api/billing/` - Billing and payments

## Deployment
The application is containerized with Docker and uses Gunicorn as the WSGI server. It runs on port 8001.

### Docker Configuration
- **Dockerfile**: Configures the Python environment and installs dependencies
- **docker-compose.yaml**: Defines the web service with environment variables and port mapping

## Key Features
1. Multi-tenant architecture with data isolation
2. Role-based access control (Superuser, Admin, Manager, Staff, Customer, Guest)
3. Comprehensive restaurant management (menu, tables, orders)
4. Hotel management add-on (rooms, bookings, services)
5. Billing and payment system with GST calculation
6. API documentation with Swagger UI
7. CORS support for frontend integration

## Dependencies
- Django
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
- Pillow
- requests
- drf-yasg
- setuptools
- python-decouple
- gunicorn
- whitenoise
- pymysql

## Environment Configuration
The application uses environment variables for configuration:
- Database connection details (MYSQL_DB_NAME, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT)
- SECRET_KEY for Django
- DEBUG flag for development/production mode
- ALLOWED_HOSTS for security

## Data Models Overview
The system uses a multi-tenant data model where each tenant has isolated data. Key relationships include:
- Tenants have Users, Food Items, Tables, Rooms, etc.
- Users can create and manage various entities
- Orders link to Tables and Food Items
- Bookings link to Rooms and Guests
- Bills connect to either Orders or Bookings