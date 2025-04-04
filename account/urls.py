from django.urls import path,include
from .views import signupView,loginView,logoutView,forgetPasswordAPIVIEW,changePassView,verifyEmailView,UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('signup/',signupView.as_view(),name="signup"),
    path("user/verify/<uid>/<token>/", verifyEmailView.as_view() ,name="verifyEmail"),
    path("login/", loginView.as_view() ,name="login"),
    path("login/refresh/", TokenRefreshView.as_view() ,name="login-refresh"),
    path("logout/", logoutView.as_view() ,name="logout"),
    path("user/forgetpass/", forgetPasswordAPIVIEW.as_view() ,name="forgorpassword"),
    path("user/changepass/<uid>/<token>/", changePassView.as_view() ,name="changepassword"),
    path("user/profile/", UserProfileView.as_view() ,name="userprofile"),
    
]