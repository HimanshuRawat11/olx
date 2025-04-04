from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import User,MyUserManager,UserProfile
# from django.contrib.auth import get_user_model


class signupSerializer(ModelSerializer):
    password2=serializers.CharField(max_length=255)
    class Meta:
        model=User
        fields=["username","email","password","password2"]
    def validate(self, attrs):
        password1=attrs.get("password")
        password2=attrs.get("password2")
        if password1!=password2:
            raise ValidationError("Confirm password and password must be same")
        return attrs
    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)  # Corrected: Use the manager's create_user method
        return user

class SignupViaNumberSerializer(ModelSerializer):
    
    class Meta:
        model=User
        fields=["phonenumber"]

class loginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate_email(self, value):
        # email=value.get("email")
        try:
            user = User.objects.get(email=value.lower())  # Ensure email is lowercase
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")
        return value
    
    def validate_password(self, value):
        """
        Ensure password is provided (You can add other password validations here).
        """
        # email=value.get("email")
        if not value:
            raise serializers.ValidationError("Password is required.")
        return value
    
# class logoutSerializer(serializers.Serializer):
    
class changepassSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        self.password=attrs.get("password")
        self.confirm_password=attrs.get("confirm_password")
        if self.password!=self.confirm_password:
            raise ValidationError("The Password and Confirm Password must match")
        return attrs 


class UserProfileSeralizer(serializers.ModelSerializer):
    
    class Meta:
        model=UserProfile
        fields="__all__"