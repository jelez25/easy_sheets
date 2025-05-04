from django.urls import path
from .views import ClassroomCreateView, ClassroomListView, ClassroomDetailView, add_student, remove_student, delete_classroom, assign_sheet, remove_sheet

urlpatterns = [
    path('', ClassroomListView.as_view(), name='classroom_list'),
    path('create/', ClassroomCreateView.as_view(), name='create_classroom'),
    path('<int:pk>/', ClassroomDetailView.as_view(), name='classroom_detail'),
    path('<int:pk>/add-student/', add_student, name='add_student'),
    path('<int:pk>/remove-student/<int:student_id>/', remove_student, name='remove_student'),
    path('<int:pk>/delete/', delete_classroom, name='delete_classroom'),
    path('<int:pk>/assign-sheet/', assign_sheet, name='assign_sheet'),
    path('<int:pk>/remove-sheet/<int:sheet_id>/', remove_sheet, name='remove_sheet'),
]