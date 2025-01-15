from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'username@gmail.com'}))
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password-input', 'placeholder': '••••••••'}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )
    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'personal_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding custom placeholders for full_name and personal_number
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'John Doe'
        })
        self.fields['personal_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '555101010'
        })

        # Remove the colon (':') from all labels
        for field in self.fields.values():
            field.label_suffix = ''

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password1 and confirm_password and password1 != confirm_password:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'personal_number')


class CustomLoginForm(forms.Form):
    email = forms.CharField(
        label='Email',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password-input', 'placeholder': 'Password'}),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Remember Me",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the colon (':') from all labels
        for field in self.fields.values():
            field.label_suffix = ''

    def clean(self):
        return super().clean()


class OTPVerificationForm(forms.Form):
    otp = forms.IntegerField(label='OTP', widget=forms.TextInput(attrs={'placeholder': 'Enter your OTP Here'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the colon (':') from all labels
        for field in self.fields.values():
            field.label_suffix = ''


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'full_name', 'personal_number', 'is_librarian']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_librarian': forms.TextInput(attrs={'class': 'form-control'}),
        }
