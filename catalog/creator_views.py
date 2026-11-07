from django.shortcuts import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .creator_serializers import ContenuGestionSerializer, ContenuProposeSerializer
from .models import Contenu
from .permissions import EstAdmin, EstCreateur


class CreatorContenuListCreateView(APIView):
    """Mes contenus (liste) et envoi d'un nouveau contenu."""

    permission_classes = [EstCreateur]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        contenus = Contenu.objects.filter(createur=request.user).select_related('matiere')
        return Response(
            ContenuGestionSerializer(contenus, many=True, context={'request': request}).data
        )

    def post(self, request):
        s = ContenuProposeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        # Toujours "en attente" et gratuit : seul un administrateur publie
        contenu = s.save(
            createur=request.user, statut=Contenu.Statut.EN_ATTENTE, premium=False
        )
        return Response(
            ContenuGestionSerializer(contenu, context={'request': request}).data, status=201
        )


class AdminContenuListView(APIView):
    """Tous les contenus, filtrables par statut : /api/admin/contenus/?statut=en_attente"""

    permission_classes = [EstAdmin]

    def get(self, request):
        contenus = Contenu.objects.select_related('matiere', 'createur')
        statut = request.query_params.get('statut')
        if statut in Contenu.Statut.values:
            contenus = contenus.filter(statut=statut)
        return Response(
            ContenuGestionSerializer(contenus, many=True, context={'request': request}).data
        )


class AdminContenuDetailView(APIView):
    """L'administrateur approuve, refuse, et choisit gratuit ou premium."""

    permission_classes = [EstAdmin]

    def patch(self, request, pk):
        contenu = get_object_or_404(Contenu, pk=pk)

        statut = request.data.get('statut')
        if statut is not None:
            if statut not in Contenu.Statut.values:
                return Response({'statut': ['Statut invalide.']}, status=400)
            contenu.statut = statut

        premium = request.data.get('premium')
        if premium is not None:
            if not isinstance(premium, bool):
                return Response({'premium': ['Valeur invalide.']}, status=400)
            contenu.premium = premium

        contenu.save()
        return Response(ContenuGestionSerializer(contenu, context={'request': request}).data)