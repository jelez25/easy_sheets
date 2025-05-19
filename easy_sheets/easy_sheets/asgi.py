"""
ASGI config for easy_sheets project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles import handlers
from channels.auth import AuthMiddlewareStack
from messaging.routing import websocket_urlpatterns
from django.urls import path, re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easy_sheets.settings')

# Obtener la aplicación ASGI base
django_asgi_app = get_asgi_application()

# Configurar el router de protocolos
if settings.DEBUG:
    # En desarrollo, usar StaticFilesHandler para servir archivos estáticos
    application = ProtocolTypeRouter({
        "http": handlers.ASGIStaticFilesHandler(django_asgi_app),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    })
else:
    # En producción, WhiteNoise se encarga de los archivos estáticos
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    })
