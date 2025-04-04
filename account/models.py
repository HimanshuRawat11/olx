from django.contrib.auth.models import AbstractBaseUser
# from django.db.models.manager import BaseManager,
from django.contrib.auth.models import BaseUserManager
import uuid
# Create your models here.
from django.db import models
from django.core.validators import RegexValidator



class MyUserManager(BaseUserManager):
    # obj.create_user('himanshu',)
    def create_user(self,username,email,password):
        
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=email.lower(),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,username,email,password):
        user = self.create_user(
        email=self.normalize_email(email),
        password=password,
        username=username,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user 

class User(AbstractBaseUser):
    id=models.UUIDField(verbose_name='uuid',primary_key=True,default=uuid.uuid4,editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255)
    phonenumber=models.CharField(max_length=10, validators=[RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits long")],null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now_add=True)
    is_verified=models.BooleanField(default=False)
    
    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username","password"]
    
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser
    
class otpHandler(models.Model):
    user_id=models.OneToOneField(User,on_delete=models.CASCADE,name="user_id")
    otp=models.IntegerField()
    created_on=models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_profile_id')
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(null=True,blank=True,max_length=200)
    age=models.IntegerField(null=True,blank=True)
    date_of_birth=models.DateField(null=True,blank=True)
    about_me=models.TextField(null=True,blank=True)
    phone_number=models.BigIntegerField(default=None)
    
    class Meta:
        db_table="userprofile"
