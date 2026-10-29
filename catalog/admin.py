from django.contrib import admin

from .models import Chapitre, Contenu, Matiere


class ChapitreInline(admin.TabularInline):
    model = Chapitre
    extra = 1


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'universite', 'niveau', 'premium')
    list_filter = ('categorie', 'universite', 'niveau', 'premium')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [ChapitreInline]


@admin.register(Contenu)
class ContenuAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type', 'matiere', 'premium', 'statut', 'createur', 'vues')
    list_filter = ('type', 'statut', 'premium', 'matiere')
    search_fields = ('titre',)
    actions = ['approuver', 'refuser']

    @admin.action(description='Approuver les contenus sélectionnés')
    def approuver(self, request, queryset):
        queryset.update(statut=Contenu.Statut.PUBLIE)

    @admin.action(description='Refuser les contenus sélectionnés')
    def refuser(self, request, queryset):
        queryset.update(statut=Contenu.Statut.REFUSE)