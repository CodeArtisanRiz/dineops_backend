from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
import os
import tempfile
from django.http import JsonResponse
from utils.permissions import IsSuperuser
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.http import FileResponse
from django.http import HttpResponseForbidden
from drf_yasg.utils import swagger_auto_schema

import logging
logger = logging.getLogger(__name__)

def home(request):
    # return HttpResponse("RMS Backend - Multi-Tenanant Accounts, Foods, POS, Analytics, and More!")
    return render(request, 'home_ui.html')