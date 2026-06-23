# PATH: Ztech/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address


class AddressInline(admin.TabularInline):
    model   = Address
    extra   = 0
    fields  = ['full_name', 'phone', 'street', 'city', 'wilaya', 'is_default']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model           = CustomUser
    list_display    = ['email', 'full_name', 'theme', 'is_staff', 'is_active', 'date_joined']
    list_filter     = ['theme', 'is_staff', 'is_active', 'subscribed_to_newsletter']
    search_fields   = ['email', 'first_name', 'last_name']
    ordering        = ['-date_joined']
    inlines         = [AddressInline]
    fieldsets = (
        ('🔐 Login',        {'fields': ('email', 'password')}),
        ('👤 Personal',     {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('🎨 Preferences',  {'fields': ('theme', 'subscribed_to_newsletter')}),
        ('🔑 Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('📅 Dates',        {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display    = ['full_name', 'user', 'city', 'wilaya', 'is_default']
    list_filter     = ['wilaya', 'is_default']
    search_fields   = ['full_name', 'user__email', 'city']