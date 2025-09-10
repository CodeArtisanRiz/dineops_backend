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

# Generate detailed markdown report
echo ""
echo "=== Generating Detailed Markdown Report ==="
{
  echo "# dineops_backend Project Context"
  echo ""
  echo "Generated on: $(date)"
  echo ""
  echo "## Project Overview"
  echo ""
  echo "dineops_backend is a comprehensive Django-based backend system for managing restaurant and hotel operations, including user management, food ordering, room bookings, and billing."
  echo ""
  echo "## Project Structure"
  echo ""
  echo "### Main Directories"
  echo ""
  find . -maxdepth 1 -type d -not -path "." -not -path "./.*" -not -path "./node_modules" -not -path "./venv" | sed 's/^\.\//  - /'
  echo ""
  echo "### App Structure"
  echo ""
  for dir in accounts billing foods hotel order; do
    if [ -d "$dir" ]; then
      echo "#### $dir/"
      find "$dir" -maxdepth 1 -type f -name "*.py" | sed 's/^\.\//  - /'
      echo ""
    fi
  done
  echo ""
  echo "## Key Files Content"
  echo ""
  
  # Capture key files with more detail
  echo "### Settings (dineops_backend/settings.py)"
  echo ""
  echo "\`\`\`python"
  grep -A 10 "INSTALLED_APPS" dineops_backend/settings.py | head -15
  echo "..."
  echo "\`\`\`"
  echo ""
  
  echo "### Main URLs (dineops_backend/urls.py)"
  echo ""
  echo "\`\`\`python"
  grep "path(" dineops_backend/urls.py | head -10
  echo "..."
  echo "\`\`\`"
  echo ""
  
  # Loop through main directories and capture key files
  for dir in accounts billing foods hotel order; do
    if [ -d "$dir" ]; then
      echo "### $dir app"
      echo ""
      
      # Models
      if [ -f "$dir/models.py" ]; then
        echo "#### Models ($dir/models.py)"
        echo ""
        echo "\`\`\`python"
        grep "^class.*models.Model" "$dir/models.py" | sed 's/(models.Model.*//'
        echo "\`\`\`"
        echo ""
      fi
      
      # Views
      if [ -f "$dir/views.py" ]; then
        echo "#### Views ($dir/views.py)"
        echo ""
        echo "\`\`\`python"
        grep "^class.*ViewSet" "$dir/views.py" | sed 's/(.*//'
        echo "\`\`\`"
        echo ""
      fi
      
      # URLs
      if [ -f "$dir/urls.py" ]; then
        echo "#### URLs ($dir/urls.py)"
        echo ""
        echo "\`\`\`python"
        head -10 "$dir/urls.py"
        echo "..."
        echo "\`\`\`"
        echo ""
      fi
      
      echo ""
    fi
  done
  
  echo "## Configuration Files"
  echo ""
  
  # Capture key configuration files
  if [ -f "requirements.txt" ]; then
    echo "### Requirements (requirements.txt)"
    echo ""
    echo "\`\`\`"
    head -10 "requirements.txt"
    echo "..."
    echo "\`\`\`"
    echo ""
  fi
  
  if [ -f "Dockerfile" ]; then
    echo "### Dockerfile"
    echo ""
    echo "\`\`\`dockerfile"
    head -15 "Dockerfile"
    echo "..."
    echo "\`\`\`"
    echo ""
  fi
  
  if [ -f "docker-compose.yaml" ]; then
    echo "### Docker Compose (docker-compose.yaml)"
    echo ""
    echo "\`\`\`yaml"
    head -15 "docker-compose.yaml"
    echo "..."
    echo "\`\`\`"
    echo ""
  fi
  
  echo "## API Endpoints"
  echo ""
  echo "### Accounts"
  echo "- GET/POST /api/accounts/users/ - User management"
  echo "- GET/POST /api/accounts/tenants/ - Tenant management"
  echo ""
  echo "### Foods"
  echo "- GET/POST /api/foods/categories/ - Food categories"
  echo "- GET/POST /api/foods/fooditems/ - Food items"
  echo ""
  echo "### Orders"
  echo "- GET/POST /api/orders/orders/ - Order processing"
  echo ""
  echo "### Hotel"
  echo "- GET/POST /api/hotel/rooms/ - Room management"
  echo "- GET/POST /api/hotel/bookings/ - Booking management"
  echo "- GET/POST /api/hotel/checkin/ - Check-in operations"
  echo "- GET/POST /api/hotel/checkout/ - Check-out operations"
  echo ""
  echo "### Billing"
  echo "- GET/POST /api/billing/bills/ - Billing operations"
  echo "- GET/POST /api/billing/bill-payments/ - Payment processing"
  echo ""
} > proj_context/detailed_report.md

# Generate comprehensive JSON context file for memory loading
echo ""
echo "=== Generating JSON Context File ==="
{
  echo "{"
  echo "  \"project_name\": \"dineops_backend\","
  echo "  \"generated_on\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"project_description\": \"Django-based backend system for managing restaurant and hotel operations\","
  echo "  \"directories\": ["
  ls -la | grep "^d" | awk '{print $9}' | grep -E "^(accounts|billing|cache|dineops|foods|hotel|order|scripts|staticfiles|templates|utils)" | sed 's/^/    "/' | sed 's/$/",/' | sed '$ s/,$//'
  echo "  ],"
  echo "  \"main_files\": ["
  ls -la | grep "^-" | grep -E "(manage.py|requirements.txt|README.md|Dockerfile|docker-compose.yaml|.env)" | awk '{print $9}' | sed 's/^/    "/' | sed 's/$/",/' | sed '$ s/,$//'
  echo "  ],"
  echo "  \"apps\": {"
  echo "    \"accounts\": {"
  echo "      \"description\": \"User and tenant management\","
  echo "      \"models\": [\"Tenant\", \"User\"],"
  echo "      \"endpoints\": [\"/api/accounts/users/\", \"/api/accounts/tenants/\"],"
  echo "      \"key_files\": [\"models.py\", \"views.py\", \"urls.py\", \"serializers.py\"]"
  echo "    },"
  echo "    \"foods\": {"
  echo "      \"description\": \"Food items and categories\","
  echo "      \"models\": [\"Category\", \"FoodItem\", \"Table\"],"
  echo "      \"endpoints\": [\"/api/foods/\"],"
  echo "      \"key_files\": [\"models.py\", \"views.py\", \"urls.py\", \"serializers.py\"]"
  echo "    },"
  echo "    \"order\": {"
  echo "      \"description\": \"Order processing\","
  echo "      \"models\": [\"Order\"],"
  echo "      \"endpoints\": [\"/api/orders/\"],"
  echo "      \"key_files\": [\"models.py\", \"views.py\", \"urls.py\", \"serializers.py\"]"
  echo "    },"
  echo "    \"hotel\": {"
  echo "      \"description\": \"Hotel room and booking management\","
  echo "      \"models\": [\"Room\", \"ServiceCategory\", \"Service\", \"Booking\", \"RoomBooking\", \"CheckIn\", \"CheckOut\", \"ServiceUsage\", \"GuestDetails\"],"
  echo "      \"endpoints\": [\"/api/hotel/\"],"
  echo "      \"key_files\": [\"models.py\", \"views.py\", \"urls.py\", \"serializers.py\"]"
  echo "    },"
  echo "    \"billing\": {"
  echo "      \"description\": \"Billing and payment processing\","
  echo "      \"models\": [\"Bill\", \"BillPayment\"],"
  echo "      \"endpoints\": [\"/api/billing/\"],"
  echo "      \"key_files\": [\"models.py\", \"views.py\", \"urls.py\", \"serializers.py\"]"
  echo "    }"
  echo "  },"
  echo "  \"deployment\": {"
  echo "    \"containerization\": \"Docker\","
  echo "    \"server\": \"Gunicorn on port 8001\","
  echo "    \"static_files\": \"WhiteNoise served from /static/\""
  echo "  },"
  echo "  \"dependencies\": {"
  echo "    \"framework\": \"Django 5.0.7\","
  echo "    \"api\": \"Django REST Framework\","
  echo "    \"authentication\": \"JWT\","
  echo "    \"documentation\": \"drf-yasg (Swagger)\","
  echo "    \"database\": \"MySQL\""
  echo "  }"
  echo "}"
} > proj_context/context.json

echo ""
echo "=== Report Generation Complete ==="
echo "Reports generated:"
echo "  - proj_context/detailed_report.md"
echo "  - proj_context/context.json"