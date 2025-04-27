from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('avatar', 'birth_date', 'role', 'school', 'name', 'surname_1', 'surname_2')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('avatar', 'birth_date', 'role', 'school', 'name', 'surname_1', 'surname_2')}),
    )
    list_display = ['username', 'email', 'name', 'surname_1', 'surname_2', 'role', 'school', 'is_staff']
    list_filter = ['role', 'school', 'is_staff', 'is_superuser', 'is_active']