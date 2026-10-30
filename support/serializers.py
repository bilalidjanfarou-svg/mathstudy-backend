from rest_framework import serializers

from .models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.SerializerMethodField()
    du_support = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = ['id', 'texte', 'created_at', 'auteur_id', 'auteur_nom', 'du_support']

    def get_auteur_nom(self, obj):
        if obj.auteur.role == 'admin':
            return 'Agent MathStudy'
        return obj.auteur.nom_complet or obj.auteur.email

    def get_du_support(self, obj):
        return obj.auteur.role == 'admin'


class TicketListSerializer(serializers.ModelSerializer):
    categorie_label = serializers.CharField(source='get_categorie_display', read_only=True)
    statut_label = serializers.CharField(source='get_statut_display', read_only=True)
    auteur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'sujet', 'categorie', 'categorie_label',
            'statut', 'statut_label', 'auteur_nom', 'created_at', 'updated_at',
        ]

    def get_auteur_nom(self, obj):
        return obj.auteur.nom_complet or obj.auteur.email


class TicketDetailSerializer(TicketListSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + ['messages']


class TicketCreateSerializer(serializers.Serializer):
    sujet = serializers.CharField(max_length=200)
    categorie = serializers.ChoiceField(choices=Ticket.Categorie.choices)
    texte = serializers.CharField(max_length=5000)