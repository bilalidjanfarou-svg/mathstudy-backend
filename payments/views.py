import re

from django.conf import settings
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Payment
from .plans import PLANS
from .serializers import PaymentSerializer
from .services import activer_abonnement


class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        # La limite ne s'applique qu'à la création d'un paiement
        if self.request.method == 'POST':
            self.throttle_scope = 'paiement'
            return [ScopedRateThrottle()]
        return []

    def get(self, request):
        paiements = Payment.objects.filter(utilisateur=request.user)
        return Response(PaymentSerializer(paiements, many=True).data)

    def post(self, request):
        plan_id = request.data.get('plan')
        moyen = request.data.get('moyen')
        telephone = re.sub(r'\s', '', str(request.data.get('telephone') or ''))

        plan = PLANS.get(plan_id)
        if not plan:
            return Response({'plan': ['Formule inconnue.']}, status=400)
        if moyen == Payment.Moyen.CARTE:
            return Response(
                {'moyen': ['Le paiement par carte n’est pas encore disponible.']}, status=400
            )
        if moyen != Payment.Moyen.MOBILE_MONEY:
            return Response({'moyen': ['Moyen de paiement invalide.']}, status=400)
        if not re.fullmatch(r'\d{8}', telephone):
            return Response({'telephone': ['Entre un numéro à 8 chiffres.']}, status=400)

        # Sans mode test explicite, on ne crée jamais d'abonnement : il faudra un vrai prestataire
        if settings.PAYMENT_MODE != 'simulation':
            return Response({'detail': 'Le paiement en ligne n’est pas encore ouvert.'}, status=503)

        with transaction.atomic():
            paiement = Payment.objects.create(
                utilisateur=request.user,
                plan=plan_id,
                montant=plan['prix'],  # le prix vient du serveur
                moyen=moyen,
                telephone_fin=telephone[-4:],
                fournisseur='simulation',
                statut=Payment.Statut.REUSSI,
            )
            activer_abonnement(request.user, plan_id)

        return Response(PaymentSerializer(paiement).data, status=201)