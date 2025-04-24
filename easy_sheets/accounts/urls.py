from django.urls import path
from .views import ProfileView, ProfileUpdate, EmailUpdate, CustomPasswordChangeView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('edit/', ProfileUpdate.as_view(), name='profile_form'),
    path('edit-email/', EmailUpdate.as_view(), name='profile_email'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='password_change'),
]