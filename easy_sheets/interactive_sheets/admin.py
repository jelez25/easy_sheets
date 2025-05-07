from django.contrib import admin
from .models import InteractiveSheet, SheetSubmission

@admin.register(InteractiveSheet)
class InteractiveSheetAdmin(admin.ModelAdmin):
    list_display = ('subject', 'creator', 'is_public', 'status', 'expiration_date')  # Fields to display in the admin list view
    list_filter = ('is_public', 'status', 'expiration_date')  # Filters for the admin sidebar
    search_fields = ('subject', 'creator__username')  # Searchable fields
    ordering = ('expiration_date',)  # Default ordering
    readonly_fields = ('creator',)  # Make the creator field read-only
    fieldsets = (
        (None, {
            'fields': ('subject', 'statement', 'base_image', 'is_public', 'expiration_date', 'status', 'creator')
        }),
        ('Interactive Options', {
            'classes': ('collapse',),
            'fields': ('interactive_options',),  # Add interactive_data here
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('grade', 'comment'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically set the creator to the logged-in user if not already set
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

@admin.register(SheetSubmission)
class SheetSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'sheet', 'status','submission_date', 'score')  # Fields to display in the admin list view
    list_filter = ('submission_date', 'score')  # Filters for the admin sidebar
    search_fields = ('student__username', 'sheet__subject')  # Searchable fields
    readonly_fields = ('submission_date',)  # Make the submission date read-only
    fieldsets = (
        (None, {
            'fields': ('student', 'sheet', 'status','answers', 'submission_date')
        }),
        ('Feedback and Scoring', {
            'classes': ('collapse',),
            'fields': ('feedback', 'score'),
        }),
    )
