#!/bin/bash

# DineOps Backend - Docker Initialization Script

echo "DineOps Backend Docker Setup"
echo "============================"

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "Building and starting services..."
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 10

echo "Running database migrations..."
docker-compose exec web python manage.py migrate

echo "Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "Setup complete!"
echo "---------------"
echo "API: http://localhost:8000/"
echo "API Documentation: http://localhost:8000/docs/"
echo "Admin Interface: http://localhost:8000/admin/"
echo ""
echo "To create a superuser, run: docker-compose exec web python manage.py createsuperuser"
echo "To stop the services, run: docker-compose down"