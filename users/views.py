from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import forms
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from requests import request

from django.views.generic.edit import FormView
from django import forms

from book_flow.models import BorrowHistory, Favorite, Book
from users.forms import CustomUserCreationForm, CustomLoginForm, OTPVerificationForm, ProfileForm
from users.models import CustomUser
from users.utils import send_verification_email


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:otp_verification')

    def form_valid(self, form):
        print(f"Redirecting to OTP verification page: {self.success_url}")
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.is_authorized = False  # Ensure authorization flag is reset
        user.save()

        # Send OTP email
        send_verification_email(user, self.request)

        # login(self.request, user)
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('users:login')
        return super(RegisterView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_message'] = messages.get_messages(self.request)
        return context


class CustomLoginView(LoginView):
    # Session-based login
    redirect_authenticated_user = True
    template_name = 'users/login.html'
    form_class = CustomLoginForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)

                # Set session expiry based on "Remember Me" checkbox
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close

                return redirect('users:home')
            # Authentication failed
            message = 'Invalid email or password. Please try again.'
            return render(request, self.template_name, {'form': form, 'message': message})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    login_url = '/users/login/'

    def get(self, request, *args, **kwargs):
        form = ProfileForm(instance=request.user)
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')  # Redirect to the profile page after updating
        return self.render_to_response({'form': form})


class MyBookShelf(LoginRequiredMixin, ListView):
    model = BorrowHistory
    template_name = 'users/my_shelf.html'
    context_object_name = 'books'
    login_url = '/users/login/'

    def get_queryset(self):
        user = self.request.user
        return BorrowHistory.objects.filter(borrower=user, returned=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorite_books'] = Favorite.objects.filter(user=self.request.user)
        context['borrowed_books'] = self.object_list.filter(issued=True)
        return context


def custom_logout_view(request):
    logout(request)
    return redirect('users:home')


class OTPVerificationView(FormView):
    template_name = 'users/otp_verification.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('users:verification_success')

    def form_valid(self, form):
        otp = form.cleaned_data['otp']
        email = self.request.session.get('verification_email')
        session_otp = self.request.session.get('verification_otp')

        if otp == session_otp:
            user = get_object_or_404(CustomUser, email=email)
            user.is_authorized = True
            user.save()

            # Clear OTP session and redirect to login
            del self.request.session['verification_otp']

            return redirect(self.success_url)

        form.add_error('otp', 'Invalid OTP.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session.get('verification_email')
        if email:
            context['email'] = email  # Pass the email to the template
        return context

    def get(self, request, *args, **kwargs):
        # If the user is already logged in, redirect to the verification success page
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'users/homepage.html'  # Template for homepage
    login_url = 'users:login'  # Redirect to login if not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.all()  # Replace with your desired queryset
        return context

