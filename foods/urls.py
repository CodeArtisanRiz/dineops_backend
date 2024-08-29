from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodItemViewSet, CategoryViewSet

app_name = 'foods'

router = DefaultRouter()
router.register(r'fooditems', FoodItemViewSet, basename='fooditem')
router.register(r'categories', CategoryViewSet, basename='category')

# urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),
    
]
