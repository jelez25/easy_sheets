from django.contrib import admin
from .models import Notebook

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'updated_at')
    search_fields = ('name', 'creator__username')
    list_filter = ('created_at', 'updated_at')
