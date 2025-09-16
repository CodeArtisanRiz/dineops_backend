#!/bin/bash
# Stop script for DineOps infrastructure services (MySQL, Redis, phpMyAdmin)

set -e

echo "Stopping DineOps Infrastructure Services"
echo "======================================="

# Stop services in reverse order
echo "Stopping phpMyAdmin..."
cd phpmyadmin && docker-compose down && cd - > /dev/null

echo "Stopping Redis..."
cd redis && docker-compose down && cd - > /dev/null

echo "Stopping MySQL..."
cd mysql && docker-compose down && cd - > /dev/null

echo ""
echo "All infrastructure services stopped successfully!"