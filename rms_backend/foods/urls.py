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
