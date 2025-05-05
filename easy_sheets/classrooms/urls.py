from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClassroomListView.as_view(), name='classroom_list'),
    path('create/', views.ClassroomCreateView.as_view(), name='create_classroom'),
    path('<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    path('<int:pk>/add-student/', views.add_student, name='add_student'),
    path('<int:pk>/remove-student/<int:student_id>/', views.remove_student, name='remove_student'),
    path('<int:pk>/delete/', views.delete_classroom, name='delete_classroom'),
    path('<int:pk>/assign-sheet/', views.assign_sheet, name='assign_sheet'),
    path('<int:pk>/remove-sheet/<int:sheet_id>/', views.remove_sheet, name='remove_sheet'),
    path('student-classroom/', views.StudentClassroomView.as_view(), name='student_classroom'),
    path('join-classroom/', views.JoinClassroomView.as_view(), name='join_classroom'),
]