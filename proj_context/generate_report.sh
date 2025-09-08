#!/bin/bash
# Project Structure Report Generator

# Change to parent directory
cd ..

echo "=== dineops_backend Project Structure Report ==="
echo "Generated on: $(date)"
echo ""

echo "=== Core Directories ==="
ls -la | grep "^d" | awk '{print $9}' | grep -E "^(accounts|billing|cache|dineops|foods|hotel|order|scripts|staticfiles|templates|utils)" | sed 's/^/  - /'

echo ""
echo "=== Main Configuration Files ==="
ls -la | grep "^-" | grep -E "(manage.py|requirements.txt|README.md|Dockerfile|docker-compose.yaml|.env)" | awk '{print $9}' | sed 's/^/  - /'

echo ""
echo "=== Django Settings ==="
cd dineops_backend
echo "  - Settings File: settings.py"
echo "  - Main URLs: urls.py"
echo "  - WSGI Application: wsgi.py"
echo "  - ASGI Application: asgi.py"
cd ..

echo ""
echo "=== Application Models Summary ==="
echo "  - accounts: Tenant, User"
echo "  - foods: Category, FoodItem, Table"
echo "  - order: Order"
echo "  - hotel: Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, GuestDetails"
echo "  - billing: Bill, BillPayment"

echo ""
echo "=== API Endpoints Summary ==="
echo "  - Authentication: /api/accounts/token/"
echo "  - User Management: /api/accounts/users/"
echo "  - Tenant Management: /api/accounts/tenants/"
echo "  - Food Items: /api/foods/fooditems/"
echo "  - Orders: /api/orders/orders/"
echo "  - Hotel (Rooms, Bookings): /api/hotel/"
echo "  - Billing: /api/billing/"

echo ""
echo "=== Deployment Configuration ==="
echo "  - Containerization: Docker (Dockerfile, docker-compose.yaml)"
echo "  - Server: Gunicorn on port 8001"
echo "  - Static Files: WhiteNoise served from /static/"

echo ""
echo "=== Report Generation Complete ==="