#!/bin/bash
# Startup script for DineOps infrastructure services (MySQL, Redis, phpMyAdmin)

set -e

# Load environment variables from the central .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "DineOps Infrastructure Services Startup Script"
echo "============================================="

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ $service_name is already running on port $port"
        return 0
    else
        echo "✗ $service_name is not running on port $port"
        return 1
    fi
}

# Function to start a service
start_service() {
    local service_dir=$1
    local service_name=$2
    local port_var=$3
    
    echo "Starting $service_name..."
    cd $service_dir
    # Use the port variable from .env
    MYSQL_PORT=${MYSQL_PORT} REDIS_PORT=${REDIS_PORT} PMA_PORT=${PMA_PORT} PMA_HOST=${PMA_HOST} \
    MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} MYSQL_DATABASE=${MYSQL_DATABASE} MYSQL_USER=${MYSQL_USER} MYSQL_PASSWORD=${MYSQL_PASSWORD} \
    docker-compose up -d
    cd - > /dev/null
    
    # Wait for service to start
    sleep 10
    
    echo "$service_name started"
}

# Check and start MySQL if needed
if ! check_service "MySQL" "${MYSQL_PORT}"; then
    echo "Starting MySQL service..."
    start_service "mysql" "MySQL" "MYSQL_PORT"
fi

# Check and start Redis if needed
if ! check_service "Redis" "${REDIS_PORT}"; then
    echo "Starting Redis service..."
    start_service "redis" "Redis" "REDIS_PORT"
fi

# Check and start phpMyAdmin if needed
if ! check_service "phpMyAdmin" "${PMA_PORT}"; then
    echo "Starting phpMyAdmin service..."
    start_service "phpmyadmin" "phpMyAdmin" "PMA_PORT"
fi

echo ""
echo "All infrastructure services started successfully!"
echo "MySQL is running on port ${MYSQL_PORT}"
echo "Redis is running on port ${REDIS_PORT}"
echo "phpMyAdmin is running on port ${PMA_PORT}"