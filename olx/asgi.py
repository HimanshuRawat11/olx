"""
ASGI config for olx project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import socketio
from django.core.asgi import get_asgi_application
from .settings import sio
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olx.settings')
django.setup()
import chats.socket 
django_asgi_app = get_asgi_application()
application=socketio.ASGIApp(sio,django_asgi_app)