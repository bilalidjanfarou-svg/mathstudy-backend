from rest_framework import serializers

from .models import Chapitre, Contenu, Matiere


def a_acces_premium(user):
    """Qui peut ouvrir les contenus premium.

    Pour l'instant, seuls les créateurs et les administrateurs.
    Quand on aura les abonnements, on vérifiera aussi la formule de l'utilisateur ici.
    """
    return bool(user and user.is_authenticated and user.role in ('creator', 'admin'))


class ContenuSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_type_display', read_only=True)
    matiere = serializers.CharField(source='matiere.nom', read_only=True)
    matiere_slug = serializers.CharField(source='matiere.slug', read_only=True)
    createur = serializers.SerializerMethodField()
    fichier = serializers.SerializerMethodField()
    verrouille = serializers.SerializerMethodField()

    class Meta:
        model = Contenu
        fields = [
            'id', 'type', 'type_label', 'titre', 'description',
            'matiere', 'matiere_slug', 'createur',
            'duree_minutes', 'pages', 'premium', 'verrouille',
            'fichier', 'vues',
        ]

    def _acces(self, obj):
        user = self.context['request'].user
        return (not obj.premium) or a_acces_premium(user)

    def get_verrouille(self, obj):
        return not self._acces(obj)

    def get_fichier(self, obj):
        # Un contenu premium n'expose jamais son fichier à quelqu'un sans accès
        if not obj.fichier or not self._acces(obj):
            return None
        return self.context['request'].build_absolute_uri(obj.fichier.url)

    def get_createur(self, obj):
        return (obj.createur.nom_complet or None) if obj.createur else None


class ChapitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapitre
        fields = ['id', 'titre', 'ordre']


class MatiereListSerializer(serializers.ModelSerializer):
    categorie_label = serializers.CharField(source='get_categorie_display', read_only=True)
    nb_ressources = serializers.SerializerMethodField()

    class Meta:
        model = Matiere
        fields = [
            'id', 'nom', 'slug', 'categorie', 'categorie_label',
            'universite', 'filiere', 'niveau', 'premium', 'nb_ressources',
        ]

    def get_nb_ressources(self, obj):
        return obj.nb_ressources()


class MatiereDetailSerializer(MatiereListSerializer):
    chapitres = ChapitreSerializer(many=True, read_only=True)
    contenus = serializers.SerializerMethodField()

    class Meta(MatiereListSerializer.Meta):
        fields = MatiereListSerializer.Meta.fields + ['description', 'chapitres', 'contenus']

    def get_contenus(self, obj):
        publies = obj.contenus.filter(statut=Contenu.Statut.PUBLIE)
        return ContenuSerializer(publies, many=True, context=self.context).data