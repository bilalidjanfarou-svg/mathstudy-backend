from django.db.models import F
from rest_framework import generics
from rest_framework.response import Response

from .models import Contenu, Matiere
from .serializers import ContenuSerializer, MatiereDetailSerializer, MatiereListSerializer


class MatiereListView(generics.ListAPIView):
    """Liste des matières, avec recherche et filtres :
    /api/matieres/?q=algo&categorie=info&universite=...&filiere=...&niveau=...
    """

    serializer_class = MatiereListSerializer

    def get_queryset(self):
        qs = Matiere.objects.all()
        p = self.request.query_params

        if q := p.get('q'):
            qs = qs.filter(nom__icontains=q)
        if categorie := p.get('categorie'):
            qs = qs.filter(categorie=categorie)
        for champ in ('universite', 'filiere', 'niveau'):
            if valeur := p.get(champ):
                qs = qs.filter(**{champ: valeur})
        return qs


class MatiereDetailView(generics.RetrieveAPIView):
    """Détail d'une matière : /api/matieres/analyse-1/"""

    queryset = Matiere.objects.all()
    serializer_class = MatiereDetailSerializer
    lookup_field = 'slug'


class ContenuDetailView(generics.RetrieveAPIView):
    """Détail d'un contenu publié : /api/contenus/3/ (compte une vue)"""

    queryset = Contenu.objects.filter(statut=Contenu.Statut.PUBLIE).select_related(
        'matiere', 'createur'
    )
    serializer_class = ContenuSerializer

    def retrieve(self, request, *args, **kwargs):
        contenu = self.get_object()
        Contenu.objects.filter(pk=contenu.pk).update(vues=F('vues') + 1)
        contenu.vues += 1
        return Response(self.get_serializer(contenu).data)