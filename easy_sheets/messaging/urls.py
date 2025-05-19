from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('conversaciones/', views.thread_list, name='thread_list'),
    path('conversacion/nueva/<int:user_id>/', views.start_thread, name='start_thread'),
    path('conversacion/<int:thread_id>/', views.thread_detail, name='thread_detail'),
]