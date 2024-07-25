from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return HttpResponse("DineOps Backend - Multi-Tenanant Accounts, Foods, POS, Analytics, and More!")