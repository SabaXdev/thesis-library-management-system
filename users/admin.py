from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['full_name', 'email', 'personal_number', 'is_librarian', 'is_authorized']
    list_filter = ['is_authorized', 'is_librarian']
    ordering = ['date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ['full_name']}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_authorized')}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'full_name',
                'password1', 'password2',
                'personal_number',
                'is_librarian', 'is_authorized'),
        }),
    )
