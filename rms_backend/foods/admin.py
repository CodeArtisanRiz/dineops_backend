from django.contrib import admin
from .models import FoodItem

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'category', 'status', 'tenant']
    list_filter = ['tenant', 'category', 'status']
    search_fields = ['name', 'description', 'category']

    def save_model(self, request, obj, form, change):
        obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)
