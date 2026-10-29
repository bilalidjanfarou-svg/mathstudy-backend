from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('MathStudy', {'fields': ('nom_complet', 'role', 'universite', 'filiere', 'niveau')}),
    )
    list_display = ('email', 'nom_complet', 'role', 'universite', 'is_staff')
    list_filter = ('role', 'universite')
    search_fields = ('email', 'nom_complet')