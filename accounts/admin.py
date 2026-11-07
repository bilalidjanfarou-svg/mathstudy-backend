from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'LearnX',
            {'fields': ('nom_complet', 'role', 'plan', 'plan_expire_le', 'universite', 'filiere', 'niveau')},
        ),
    )
    list_display = ('email', 'nom_complet', 'role', 'plan', 'plan_expire_le', 'universite', 'is_staff')
    list_filter = ('role', 'plan', 'universite')
    search_fields = ('email', 'nom_complet')