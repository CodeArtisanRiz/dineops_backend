from django.contrib import admin
from .models import FoodItem


# Register your models here.
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'tenant']
    list_filter = ['tenant']
    search_fields = ['name', 'description']

    def save_model(self, request, obj, form, change):
        # Assign current user's tenant to the food item's tenant field when saving via admin
        obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)
