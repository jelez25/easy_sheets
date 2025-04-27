from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateSheetView.as_view(), name='create_sheet'),
    path('my-sheets/', views.TeacherSheetsView.as_view(), name='teacher_sheets'),
    path('<int:pk>/', views.SheetDetailView.as_view(), name='sheet_detail'),
    path('api/sheet/<int:sheet_id>/interactive-options/', views.interactive_options_api, name='interactive_options_api'),
]