"""
URL configuration for easy_sheets project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from easy_sheets.views import home_page
import os
from accounts.views import SignUpView
from django.contrib.auth.views import LogoutView, LoginView
from django.views.static import serve as media_serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('register/', SignUpView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('profile/', include('accounts.urls')),
    path('sheets/', include('interactive_sheets.urls')),
    path('classrooms/', include('classrooms.urls')),  # Incluir las rutas de classrooms
    path('notebooks/', include('notebooks.urls')),
    path('messaging/', include('messaging.urls')),  # Incluir las rutas de messaging
]


if settings.DEBUG:
    # Servir archivos estáticos usando whitenoise
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Servir archivos de media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)