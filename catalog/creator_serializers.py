from rest_framework import serializers

from .models import Contenu, Matiere

EXTENSIONS = {
    'video': ('.mp4', '.webm'),
    'pdf': ('.pdf',),
    'exercice': ('.pdf',),
    'correction': ('.pdf',),
    'examen': ('.pdf',),
}
TAILLE_VIDEO = 300 * 1024 * 1024  # 300 Mo
TAILLE_PDF = 20 * 1024 * 1024  # 20 Mo


class ContenuProposeSerializer(serializers.ModelSerializer):
    """Vérifie le contenu envoyé par un créateur."""

    matiere = serializers.SlugRelatedField(slug_field='slug', queryset=Matiere.objects.all())

    class Meta:
        model = Contenu
        fields = ['type', 'titre', 'description', 'matiere', 'fichier', 'duree_minutes', 'pages']
        extra_kwargs = {'fichier': {'required': True, 'allow_empty_file': False}}

    def validate(self, data):
        fichier, type_ = data['fichier'], data['type']
        autorisees = EXTENSIONS[type_]
        if not fichier.name.lower().endswith(autorisees):
            raise serializers.ValidationError(
                {'fichier': f'Format non accepté. Envoie un fichier {" ou ".join(autorisees)}.'}
            )
        limite = TAILLE_VIDEO if type_ == 'video' else TAILLE_PDF
        if fichier.size > limite:
            raise serializers.ValidationError(
                {'fichier': f'Fichier trop lourd ({limite // (1024 * 1024)} Mo maximum).'}
            )
        return data


class ContenuGestionSerializer(serializers.ModelSerializer):
    """Affichage d'un contenu pour le créateur et pour l'administrateur."""

    type_label = serializers.CharField(source='get_type_display', read_only=True)
    statut_label = serializers.CharField(source='get_statut_display', read_only=True)
    matiere = serializers.CharField(source='matiere.nom', read_only=True)
    createur = serializers.SerializerMethodField()
    fichier = serializers.SerializerMethodField()

    class Meta:
        model = Contenu
        fields = [
            'id', 'titre', 'type', 'type_label', 'matiere', 'createur',
            'statut', 'statut_label', 'premium', 'vues', 'fichier', 'created_at',
        ]

    def get_createur(self, obj):
        if not obj.createur:
            return '—'
        return obj.createur.nom_complet or obj.createur.email

    def get_fichier(self, obj):
        request = self.context.get('request')
        if obj.fichier and request:
            return request.build_absolute_uri(obj.fichier.url)
        return None