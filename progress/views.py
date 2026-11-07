from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Contenu, Matiere
from catalog.serializers import a_acces_premium

from .models import Progression


def item(contenu, user):
    return {
        'id': contenu.id,
        'titre': contenu.titre,
        'type': contenu.type,
        'matiere': contenu.matiere.nom,
        'matiere_slug': contenu.matiere.slug,
        'verrouille': contenu.premium and not a_acces_premium(user),
    }


class ProgressionView(APIView):
    """Enregistre qu'un contenu a été ouvert, et éventuellement terminé."""

    permission_classes = [IsAuthenticated]

    def post(self, request, contenu_id):
        contenu = get_object_or_404(Contenu, pk=contenu_id, statut=Contenu.Statut.PUBLIE)
        if contenu.premium and not a_acces_premium(request.user):
            return Response({'detail': 'Contenu réservé aux abonnés.'}, status=403)

        progression, _ = Progression.objects.get_or_create(
            utilisateur=request.user, contenu=contenu
        )
        termine = request.data.get('termine')
        if termine is not None:
            if not isinstance(termine, bool):
                return Response({'termine': ['Valeur invalide.']}, status=400)
            progression.termine = termine
        progression.save()  # met à jour la date de dernière vue
        return Response({'termine': progression.termine})


class DashboardView(APIView):
    """Les données du tableau de bord de l'étudiant connecté."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        publies = Contenu.objects.filter(statut=Contenu.Statut.PUBLIE).select_related('matiere')
        progressions = list(
            Progression.objects.filter(utilisateur=user, contenu__statut=Contenu.Statut.PUBLIE)
            .select_related('contenu__matiere')
        )  # déjà triées de la plus récente à la plus ancienne

        # Dernier contenu consulté
        recent = None
        if progressions:
            c = progressions[0].contenu
            recent = {**item(c, user), 'type_label': c.get_type_display()}

        # Matières suivies : celles où l'étudiant a ouvert au moins un contenu
        derniere = {}
        for p in progressions:
            derniere.setdefault(p.contenu.matiere_id, p.derniere_vue)
        suivies = sorted(
            Matiere.objects.filter(id__in=derniere), key=lambda m: derniere[m.id], reverse=True
        )[:6]

        matieres = []
        total_global, faits_global = 0, 0
        for m in suivies:
            total = publies.filter(matiere=m).count()
            faits = sum(1 for p in progressions if p.contenu.matiere_id == m.id and p.termine)
            total_global += total
            faits_global += faits
            matieres.append(
                {
                    'nom': m.nom,
                    'slug': m.slug,
                    'total': total,
                    'termines': faits,
                    'pourcentage': round(100 * faits / total) if total else 0,
                }
            )

        vus = [p.contenu_id for p in progressions]
        termines = [p.contenu_id for p in progressions if p.termine]

        recommandees = publies.filter(type='video').exclude(id__in=vus).order_by('-vues')[:3]
        derniers_pdf = publies.filter(type='pdf').order_by('-created_at')[:3]
        exercices = publies.filter(type='exercice').exclude(id__in=termines).order_by('-created_at')[:3]

        return Response(
            {
                'progression_globale': round(100 * faits_global / total_global) if total_global else 0,
                'recent': recent,
                'matieres': matieres,
                'recommandees': [item(c, user) for c in recommandees],
                'derniers_pdf': [item(c, user) for c in derniers_pdf],
                'exercices': [item(c, user) for c in exercices],
            }
        )