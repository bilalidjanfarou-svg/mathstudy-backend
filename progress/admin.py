from django.contrib import admin

from .models import Progression


@admin.register(Progression)
class ProgressionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'contenu', 'termine', 'derniere_vue')
    list_filter = ('termine',)
    search_fields = ('utilisateur__email', 'contenu__titre')