# DineOps Backend - Docker Setup

This document explains how to set up and run the DineOps backend using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- An existing MySQL database (externally hosted)

## Setup Instructions

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd DineOps_backend
   ```

2. **Environment Configuration**:
   Update the `.env` file with your database connection details:
   ```bash
   # Django settings
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=*

   # Database settings (update with your actual database credentials)
   MYSQL_DB_NAME=your_database_name
   MYSQL_HOST=your_database_host
   MYSQL_USER=your_database_user
   MYSQL_PASSWORD=your_database_password
   MYSQL_PORT=3306
   ```

3. **Build and Run the Service**:
   ```bash
   docker-compose up --build
   ```

   This will start the Django application service and connect to your existing MySQL database.

4. **Database Migration** (First time only):
   In a new terminal, run the database migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a Superuser** (Optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Collect Static Files** (if not already done during build):
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## Accessing the Application

- **API**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs/
- **Admin Interface**: http://localhost:8000/admin/

## Stopping the Service

To stop the service:
```bash
docker-compose down
```

## Development Workflow

1. **Making Changes to the Code**:
   - The code is mounted as a volume in the Docker container, so changes to the code will be reflected immediately.
   - If you add new dependencies, you'll need to rebuild the image:
     ```bash
     docker-compose build
     ```

2. **Running Management Commands**:
   You can run any Django management command using:
   ```bash
   docker-compose exec web python manage.py <command>
   ```

## Troubleshooting

1. **Port Conflicts**:
   If you get port conflicts, you can change the ports in `docker-compose.yml`.

2. **Permission Issues**:
   If you encounter permission issues, make sure the Docker daemon is running and your user has the necessary permissions.

3. **Database Connection Issues**:
   Make sure your database is accessible from the Docker container and the environment variables are correctly set.

4. **Firewall Issues**:
   If your database is behind a firewall, make sure it allows connections from your Docker host.