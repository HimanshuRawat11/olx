from .models import User,otpHandler,UserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import signupSerializer,loginSerializer,changepassSerializer,UserProfileSeralizer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework_simplejwt.tokens import Token
from django.contrib.auth import authenticate
from datetime import datetime,timedelta,timezone
from .permissions import IsVerified
from django.core.mail import send_mail
from olx import settings
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from base64 import urlsafe_b64decode,urlsafe_b64encode
from django.utils.encoding import force_bytes,force_str



def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class signupView(APIView):
    http_method_names=['post']
    
    def post(self,request):
        data=request.data
        serializer=signupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user=User.objects.get(email=serializer.validated_data["email"])
            address = user.email
            subject = "Verify Email "
            uid=urlsafe_b64encode(force_bytes(user.pk))
            token=default_token_generator.make_token(user)
                    
            url = request._current_scheme_host+'/account/user/verify/'+uid.decode('utf-8') +'/'+token+'/'
            message = f'''Click on the link to reset the Password
                        Link:{url}'''
            try:
                send_mail(subject,message,settings.EMAIL_HOST_USER,[address])
                return Response({"message":"Please click on the link sent on email to verify the email"})
            except:
                return Response("There was an error while sending email",status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
# class signupNumberView(APIView):
    
        
        
class verifyEmailView(APIView):
    
    http_method_names=['get']
    def get(self,request,uid,token):
        try:
            decoded_bytes = urlsafe_b64decode(uid)
            decoded_string = decoded_bytes.decode('utf-8', errors='ignore')
            users = User.objects.get(id=decoded_string)
            if not users:
                return Response({"message":"There is no user"})
            if not default_token_generator.check_token(users,token):
                return Response({"message":"The link expired"})
            users.is_verified=True
            users.save()
            return Response("The id was verified.Now you can login")
        except Exception as e:
            return Response({"Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class loginView(APIView):
    permission_classes=[IsVerified]
    http_method_names=['get']
    def get(self,request):         
        serializerr=loginSerializer(data=request.data)
        if serializerr.is_valid(raise_exception=True):
            user1=authenticate(email=serializerr.data.get("email"),password=serializerr.data.get("password"))
            if not user1:
                return Response({"message":"Invalid Credetials"},status=status.HTTP_403_FORBIDDEN)
            user1.last_login=datetime.now()
            user1.save()
            refresh = get_tokens_for_user(user1)
            return Response({"message":"Succesfully logged in","Token":refresh},status=status.HTTP_200_OK)
        return Response({"message":serializerr.errors},status=status.HTTP_400_BAD_REQUEST)


class forgetPasswordAPIVIEW(APIView):
    
    permission_classes=[IsVerified]
    user=User.objects
    
    def post(self,request):
        data=request.data
        user_details=self.user.get(email=data["email"])

        address = data['email']
        subject = "Reset Password "
        uid=urlsafe_b64encode(force_bytes(user_details.pk))
        token=default_token_generator.make_token(user_details)
                
        url = request._current_scheme_host+'/account/user/changepass/'+uid.decode('utf-8') +'/'+token+'/'
        message = f'''Click on the link to reset the Password
                    Link:{url}'''
        
        with transaction.atomic():
            if address and subject and message:
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                    return Response("Email sent successfully")
                except Exception as e:
                    return Response("There was an error sending the email")
            return Response("Please enter a valid email")
        
    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"detail": "You must verify your account to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, User.DoesNotExist):
            return Response(
                {"detail": "There is no user registered wuth this email."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)
        
        
        
        
class changePassView(APIView):
    
    http_method_names=['post']
    user=User.objects
    
    def post(self,request,uid,token):
        try:
            decoded_bytes = urlsafe_b64decode(uid)
            decoded_string = decoded_bytes.decode('utf-8', errors='ignore')
            users = self.user.get(id =decoded_string)
            if not users:
                return Response("Invalid Link")
            serializer=changepassSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if not default_token_generator.check_token(users,token):
                    return Response("The link has expired")
                users.set_password(request.data.get("password"))
                users.save()
                return Response("Password changed successfully")
            return Response(serializer.errors)
        except Exception as e:
            return Response(f"{e}")
        
        
class logoutView(APIView):
    
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    http_method_names=['post']
    
    def post(self,request):
        print(request.user)
        try:
            refreshtoken=request.data["refresh_token"]
            token_blacklist=RefreshToken(refreshtoken)
            token_blacklist.blacklist()
            return Response({"message":"The token was Flushed"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":"There was an error wile flushing the ",
                             "Error Message":f"{e}"},status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    http_method_names=["post"]
    
    def post(self,request):
        data=request.data
        userid=request.user.id
        # data["user"]=userid
        try:
            if UserProfile.objects.filter(user_id=userid).exists():
                user=UserProfile.objects.get(user_id=userid)
                for key,val in data.items():
                    setattr(user,key,val)
                user.save()
                # serializer=UserProfileSeralizer(user,data)
            else:
                serializer=UserProfileSeralizer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message":"User Profile updated"},status=status.HTTP_200_OK)
                return Response(serializer.errors)
            return Response("Error")
        except Exception as e:
            return Response({"message":f"Error Occured {e}"},status=status.HTTP_400_BAD_REQUEST)
        