"""
WSGI config for olx project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""



import os
import django
# from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
import socketio
from olx.settings import sio  

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "olx.settings")
# django.setup()

django_asgi_app = get_wsgi_application()
# application = socketio.WSGIApp(sio, django_asgi_app,socketio_path= 'socket.io')
