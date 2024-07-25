from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Tenant

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'tenant', 'is_staff', 'is_superuser')
    list_filter = ('tenant', 'is_staff', 'is_superuser', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address')
    ordering = ('username',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_active', 'role', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Tenant Info', {'fields': ('tenant',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Tenant)

admin.site.unregister(Group)
