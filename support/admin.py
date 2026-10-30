from django.contrib import admin

from .models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'auteur', 'categorie', 'statut', 'updated_at')
    list_filter = ('statut', 'categorie')
    search_fields = ('sujet', 'auteur__email')
    inlines = [TicketMessageInline]