from django.http import HttpResponse
from django.shortcuts import render
import os
from django.http import JsonResponse
from utils.permissions import IsSuperuser
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.http import FileResponse
from django.http import HttpResponseForbidden
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(method='get', tags=['System'])
@api_view(['GET'])
@permission_classes([IsSuperuser])  # Superuser Only
def list_root_files(request):
    # Get the root dir
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # List files and folders in the root dir
    items = []
    for item_name in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item_name)
        if os.path.isfile(item_path):
            items.append({'name': item_name, 'type': 'file'})
        elif os.path.isdir(item_path):
            items.append({'name': item_name, 'type': 'folder'})
    
    return JsonResponse({'items': items})

@swagger_auto_schema(method='get', tags=['System'])
@api_view(['GET'])
@permission_classes([IsSuperuser])  # Superuser Only
def download_db(request):
    # Path to the db
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')

    # Ensure the file exists
    if not os.path.exists(db_path):
        return HttpResponseForbidden("Database file not found.")

    # Serve the file as response
    response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename='db.sqlite3')

    return response

def home(request):
    # return HttpResponse("RMS Backend - Multi-Tenanant Accounts, Foods, POS, Analytics, and More!")
    return render(request, 'home_ui.html')

def download_db_page(request):
    # Add a tag for UI-related endpoints
    return render(request, 'db_backup.html')
