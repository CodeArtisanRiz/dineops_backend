# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import FoodItemViewSet

# router = DefaultRouter()
# router.register(r'fooditems', FoodItemViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]
# foods/urls.py

# from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns
# from .views import FoodItemViewSet

# app_name = 'foods'

# urlpatterns = [
#     path('fooditems/', FoodItemViewSet.as_view({'get': 'list'}), name='fooditem-list'),
#     path('fooditems/<int:pk>/', FoodItemViewSet.as_view({'get': 'retrieve'}), name='fooditem-detail'),
# ]

# urlpatterns = format_suffix_patterns(urlpatterns)

# foods/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodItemViewSet

app_name = 'foods'

router = DefaultRouter()
router.register(r'fooditems', FoodItemViewSet, basename='fooditem')

# urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),
]
