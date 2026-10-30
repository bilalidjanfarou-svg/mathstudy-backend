from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('MathStudy', {'fields': ('nom_complet', 'role', 'plan', 'universite', 'filiere', 'niveau')}),
    )
    list_display = ('email', 'nom_complet', 'role', 'plan', 'universite', 'is_staff')
    list_filter = ('role', 'plan', 'universite')
    search_fields = ('email', 'nom_complet')