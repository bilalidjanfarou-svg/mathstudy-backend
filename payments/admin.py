from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'utilisateur', 'plan', 'montant', 'moyen', 'statut', 'fournisseur', 'created_at')
    list_filter = ('statut', 'plan', 'moyen', 'fournisseur')
    search_fields = ('reference', 'utilisateur__email')
    readonly_fields = [f.name for f in Payment._meta.fields]

    def has_add_permission(self, request):
        return False