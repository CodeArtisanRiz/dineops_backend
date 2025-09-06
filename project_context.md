# DineOps Backend - Project Context

## Project Overview
A multi-tenant restaurant management system built with Django and Django REST framework for the backend. It includes user authentication, food management features, and tenant-specific data management. Future features will include hotel management, POS functionality, and real-time data updates.

## Technologies Used
- **Framework**: Django 5.0.7
- **Database**: MySQL (with plans to port to MongoDB Atlas)
- **Authentication**: Django REST Framework Simple JWT
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Other Technologies**: 
  - Django CORS Headers
  - Pillow
  - Requests
  - Python Decouple
  - Gunicorn
  - WhiteNoise
  - PyMySQL

## Core Features
- User authentication with token management (access and refresh tokens)
- Tenant-specific data isolation
- CRUD operations for food items
- Multi-tenant architecture
- Support for optional hotel management add-on
- Real-time data updates (planned)

## Application Structure

### 1. Accounts App
**Purpose**: User and tenant management

**Models**:
- **Tenant**: Manages tenant information
  - Key fields: tenant_name, has_hotel_feature, total_tables, address fields, contact information, gst_no, logo, subscription dates, GST rates
- **User** (extends AbstractUser): Custom user model
  - Key fields: username, email, role (superuser, admin, manager, staff, customer, guest), tenant (foreign key), phone, address fields, dob

### 2. Foods App
**Purpose**: Food item and category management

**Models**:
- **Category**: Food categories
  - Key fields: tenant (foreign key), name, description, image, status
- **FoodItem**: Individual food items
  - Key fields: tenant (foreign key), name, description, price, image, category (foreign key), veg (boolean), status
- **Table**: Restaurant tables
  - Key fields: tenant (foreign key), table_number, occupied (boolean), order (integer)

### 3. Order App
**Purpose**: Order management

**Models**:
- **Order**: Customer orders
  - Key fields: tenant (foreign key), customer (foreign key to User), status (in_progress, on_hold, kot, served, settled, cancelled), order_type (take_away, dine_in, delivery, online, hotel), tables (many-to-many to Table), room_id (foreign key to Room), booking_id (foreign key to Booking), food_items (many-to-many to FoodItem), quantity, notes, kot_count, total

### 4. Hotel App
**Purpose**: Hotel management features

**Models**:
- **Room**: Hotel rooms
  - Key fields: room_number, room_type, beds, amenities, price, description, image, tenant (foreign key), status (available, maintenance, cleaning)
- **ServiceCategory**: Service categories
- **Service**: Hotel services
- **Booking**: Room bookings
  - Key fields: tenant (foreign key), booking_date, status, guests (many-to-many to User), advance, total_amount, id_card
- **RoomBooking**: Links rooms to bookings
- **CheckIn**: Guest check-ins
- **CheckOut**: Guest check-outs
- **ServiceUsage**: Service usage tracking
- **GuestDetails**: Additional guest information

### 5. Billing App
**Purpose**: Billing and payment management

**Models**:
- **Bill**: Billing records
  - Key fields: tenant (foreign key), bill_no, bill_type (HOT for Hotel, RES for Restaurant), customer_gst, order_id (foreign key to Order), booking_id (foreign key to Booking), total, discount, gst breakdown fields, sgst_amount, cgst_amount, net_amount, status (cancelled, unpaid, paid, partial)
- **BillPayment**: Individual payments
  - Key fields: bill_id (foreign key to Bill), bill_amount, paid_amount, payment_method (cash, card, upi, net_banking, other), payment_date, payment_details

## API Endpoints

### Authentication Endpoints
- **POST** `/api/accounts/token/` - Obtain a new access and refresh token (Public)
- **POST** `/api/accounts/token/refresh/` - Refresh the access token using the refresh token (Public)

### Tenant Endpoints
- **POST** `/api/accounts/tenants/` - Create a new tenant (Superuser)
- **GET** `/api/accounts/tenants/` - Retrieve a list of all tenants (Superuser/Manager/Staff)
- **GET** `/api/accounts/tenants/{id}/` - Retrieve details of a specific tenant (Superuser)
- **PUT** `/api/accounts/tenants/{id}/` - Update details of a specific tenant (Superuser)
- **DELETE** `/api/accounts/tenants/{id}/` - Delete a specific tenant (Superuser)

### Table Endpoints
- **GET** `/api/accounts/tables/` - Retrieve a list of tables (Superuser/Admin/Manager)
- **GET** `/api/accounts/tables/{id}/` - Retrieve details of a specific table (Superuser/Admin/Manager)
- **POST** `/api/accounts/tables/` - Create a table (Superuser/Admin/Manager)
- **PUT** `/api/accounts/tables/{id}/` - Update a table (Superuser/Admin/Manager)
- **DELETE** `/api/accounts/tables/{id}/` - Delete a table (Superuser/Admin/Manager)

### User Endpoints
- **POST** `/api/accounts/users/` - Create a new user (Superuser/Admin/Manager)
- **GET** `/api/accounts/users/` - Retrieve a list of users (Superuser/Admin/Manager)
- **GET** `/api/accounts/users/{id}/` - Retrieve details of a specific user (Superuser/Admin/Manager)
- **PUT** `/api/accounts/users/{id}/` - Update details of a specific user (Superuser/Admin/Manager)
- **DELETE** `/api/accounts/users/{id}/` - Delete a specific user (Superuser/Admin/Manager)

### Food Item Endpoints
- **POST** `/api/foods/fooditems/` - Create a new food item (Superuser/Admin/Manager)
- **GET** `/api/foods/fooditems/` - Retrieve a list of food items (Admin/Manager/Superuser)
- **GET** `/api/foods/fooditems/{id}/` - Retrieve details of a specific food item (Admin/Manager/Superuser)
- **PUT** `/api/foods/fooditems/{id}/` - Update details of a specific food item (Superuser/Admin/Manager)
- **DELETE** `/api/foods/fooditems/{id}/` - Delete a specific food item (Superuser/Admin/Manager)

## Deployment Configuration
- **Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Environment Variables**:
  - SECRET_KEY
  - DEBUG
  - ALLOWED_HOSTS
  - MYSQL_DB_NAME
  - MYSQL_USER
  - MYSQL_PASSWORD
  - MYSQL_HOST
  - MYSQL_PORT

## Authentication Settings
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Auth Header Types**: Bearer