from django.shortcuts import render
from .models import Chat, Message,GroupAdmin
from account.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListAPIView
# Create your views here.

