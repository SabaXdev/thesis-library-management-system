from django.urls import path
from django.views.generic import TemplateView

from book_flow.views import BookList
from users.views import (RegisterView, CustomLoginView, custom_logout_view,
                         ProfileView, OTPVerificationView, MyBookShelf, HomePageView)
app_name = 'users'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('my_shelf/', MyBookShelf.as_view(), name='my_shelf'),
    # OTP verification
    path('otp-verification/', OTPVerificationView.as_view(), name='otp_verification'),
    path('verification-success/', TemplateView.as_view(template_name="users/verification_success.html"),
         name='verification_success'),

]
