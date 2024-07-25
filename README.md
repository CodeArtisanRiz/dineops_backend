# Restaurant Management System Backend - API

## Project Overview
This project is a multi-tenant restaurant management system built with Django and Django REST framework for the backend. It includes user authentication, food management features, and tenant-specific data management. Future features will include hotel management, POS functionality, and real-time data updates.

### Key Features
- User authentication with token management (access and refresh tokens)
- Tenant-specific data isolation
- CRUD operations for food items
- Multi-tenant architecture
- Support for optional hotel management add-on
- SQLite database (with plans to port to MongoDB Atlas)
- Real-time data updates (planned)

## Endpoints and Permissions

### Authentication Endpoints

#### Obtain Token
- **URL**: `/api/accounts/token/`
- **Method**: `POST`
- **Permissions**: Public
- **Description**: Obtain a new access and refresh token.
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

#### Refresh Token
- **URL**: `/api/accounts/token/refresh/`
- **Method**: `POST`
- **Permissions**: Public
- **Description**: Refresh the access token using the refresh token.
- **Request Body**:
  ```json
  {
    "refresh": "string"
  }
  ```

### Tenant Endpoints

#### Create Tenant
- **URL:** `/api/accounts/tenants/`
- **Method:** `POST`
- **Permissions:** Superuser
- **Description:** Create a new tenant.
- **Request Body:**
  ```json
  {
    "tenant_name": "string",
    "domain_url": "string"  // Optional
  }
  ```

#### List Tenants
- **URL:** `/api/accounts/tenants/`
- **Method:** `GET`
- **Permissions:** Superuser
- **Description:** Retrieve a list of all tenants.

#### Retrieve Tenant
- **URL:** `/api/accounts/tenants/{id}/`
- **Method:** `GET`
- **Permissions:** Superuser
- **Description:** Retrieve details of a specific tenant.

#### Update Tenant
- **URL:** `/api/accounts/tenants/{id}/`
- **Method:** `PUT`
- **Permissions:** Superuser
- **Description:** Update details of a specific tenant.
- **Request Body:**
  ```json
  {
    "tenant_name": "string",
    "domain_url": "string"  // Optional
  }
  ```

#### Delete Tenant
- **URL:** `/api/accounts/tenants/{id}/`
- **Method:** `DELETE`
- **Permissions:** Superuser
- **Description:** Delete a specific tenant.

### User Endpoints

#### Create User
- **URL:** `/api/accounts/users/`
- **Method:** `POST`
- **Permissions:** Superuser/Admin/Manager [Superuser can create admins and manager and admins can create manager, not vice versa. Also staff and customer can be created by all 3]
- **Description:** Create a new user.
- **Request Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "tenant": "integer",  // Optional if not superuser.
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "phone": "string",
    "address": "string"
  }
  ```

#### List Users
- **URL:** `/api/accounts/users/`
- **Method:** `GET`
- **Permissions:** Superuser, Admin (limited to associated tenant data), Manager (limited to associated tenant data)
- **Description:** Retrieve a list of users. Superusers can view all users, while Admins and Managers can only see users within their tenant.

#### Retrieve User
- **URL:** `/api/accounts/users/{id}/`
- **Method:** `GET`
- **Permissions:** Superuser, Admin (limited to associated tenant data), Manager (limited to associated tenant data)
- **Description:** Retrieve details of a specific user.

#### Update User
- **URL:** `/api/accounts/users/{id}/`
- **Method:** `PUT`
- **Permissions:** Superuser/Admin/Manager [Superuser can update admins and manager and admins can update manager, not vice versa. Also staff and customer can be updated by all 3]
- **Description:** Update details of a specific user.
- **Request Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "tenant": "integer",  // Optional if superuser.
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "phone": "string",
    "address": "string"
  }
  ```

#### Delete User
- **URL:** `/api/accounts/users/{id}/`
- **Method:** `DELETE`
- **Permissions:** Superuser/Admin/Manager [Superuser can delete admins and manager and admins can delete manager, not vice versa. Also staff and customer can be deleted by all 3]
- **Description:** Delete a specific user.

### Food Item Endpoints

#### Create Food Item
- **URL:** `/api/foods/fooditems/`
- **Method:** `POST`
- **Permissions:** Superuser[required tenant id], Admin, Manager
- **Description:** Create a new food item.
- **Request Body:**
  ```json
  {
    "tenant": "integer",  // Optional if not superuser
    "name": "string",
    "description": "string",
    "price": "decimal",
    "image": "file",
    "category": "string",
    "status": "string",  // 'enabled' or 'disabled'
    "tenant": "integer"  // Required if superuser
  }
  ```

#### List Food Items
- **URL:** `/api/foods/fooditems/`
- **Method:** `GET`
- **Permissions:** Admin/Manager (limited to associated tenant data), Superuser (all data)
- **Description:** Retrieve a list of food items.

#### Retrieve Food Item
- **URL:** `/api/foods/fooditems/{id}/`
- **Method:** `GET`
- **Permissions:** Admin/Manager (limited to associated tenant data), Superuser (all data)
- **Description:** Retrieve details of a specific food item.

#### Update Food Item
- **URL:** `/api/foods/fooditems/{id}/`
- **Method:** `PUT`
- **Permissions:** Superuser, Admin, Manager
- **Description:** Update details of a specific food item.
- **Request Body:**
  ```json
  {
    "tenant": "integer",  // Optional if not superuser.
    "name": "string",
    "description": "string",
    "price": "decimal",
    "image": "file",
    "category": "string",
    "status": "string"  // 'enabled' or 'disabled'
  }
  ```

#### Delete Food Item
- **URL:** `/api/foods/fooditems/{id}/`
- **Method:** `DELETE`
- **Permissions:** Superuser, Admin, Manager
- **Description:** Delete a specific food item.

### Authentication Endpoints

#### Obtain Token
- **URL:** `/api/token/`
- **Method:** `POST`
- **Permissions:** Public
- **Description:** Obtain an access and refresh token.
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

#### Refresh Token
- **URL:** `/api/token/refresh/`
- **Method:** `POST`
- **Permissions:** Public
- **Description:** Refresh the access token using a refresh token.
- **Request Body:**
  ```json
  {
    "refresh": "string"
  }
  ```