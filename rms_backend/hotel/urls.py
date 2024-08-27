# hotel/urls.py

from django.urls import path
from .views import (
    RoomListCreateView, 
    RoomDetailView, 
    # ReservationListCreateView, 
    # ReservationDetailView
)

urlpatterns = [
    path('rooms/', RoomListCreateView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    # path('reservations/', ReservationListCreateView.as_view(), name='reservation-list'),
    # path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
]
