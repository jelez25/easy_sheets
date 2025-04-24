from django.urls import path
from .views import CreateSheetView, TeacherSheetsView, SheetDetailView, SheetEditView

urlpatterns = [
    path('create/', CreateSheetView.as_view(), name='create_sheet'),
    path('my-sheets/', TeacherSheetsView.as_view(), name='teacher_sheets'),
    path('<int:pk>/', SheetDetailView.as_view(), name='sheet_detail'),
    #path('<int:pk>/edit/', SheetEditView.as_view(), name='sheet_edit'),
]