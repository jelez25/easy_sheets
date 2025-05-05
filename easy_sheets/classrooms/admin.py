from django.contrib import admin
from .models import Classroom

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_code', 'teacher', 'created_at')  # Columns to display in the admin list view
    list_filter = ('teacher', 'created_at')  # Filters for the admin sidebar
    search_fields = ('name', 'class_code', 'teacher__username')  # Search bar fields
    ordering = ('-created_at',)  # Default ordering
    filter_horizontal = ('students', 'sheets')  # For ManyToMany fields
