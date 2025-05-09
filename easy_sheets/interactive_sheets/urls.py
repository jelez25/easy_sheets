from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateSheetView.as_view(), name='create_sheet'),
    path('teacher-sheets/', views.TeacherSheetsView.as_view(), name='teacher_sheets'),
    path('<int:pk>/', views.SheetDetailView.as_view(), name='sheet_detail'),
    path('api/sheet/<int:sheet_id>/interactive-options/', views.interactive_options_api, name='interactive_options_api'),
    path('student-sheets/', views.StudentSheetsView.as_view(), name='student_sheets'),
    path('no-permission/', views.NoPermissionView.as_view(), name='no_permission'),
    path('submit-sheet/<int:sheet_id>/', views.submit_sheet, name='submit_sheet'),
    path('sheet/<int:sheet_id>/submissions/', views.SheetSubmissionsView.as_view(), name='sheet_submissions'),
    path('submission/<int:sheet_id>/', views.view_submission, name='view_submission'),
    path('api/sheet/<int:sheet_id>/correction/', views.submission_correction_api, name='submission_correction_api'),
]