from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Contenu
from catalog.permissions import EstAdmin
from payments.models import Payment
from payments.serializers import PaymentSerializer

from .models import User


class AdminUserSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source='plan_effectif', read_only=True)
    plan_label = serializers.CharField(source='plan_label_effectif', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'nom_complet', 'universite', 'role',
            'plan', 'plan_label', 'plan_expire_le', 'date_joined',
        ]


class AdminPaymentSerializer(PaymentSerializer):
    utilisateur = serializers.SerializerMethodField()

    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + ['utilisateur']

    def get_utilisateur(self, obj):
        return obj.utilisateur.nom_complet or obj.utilisateur.email


class AdminStatsView(APIView):
    permission_classes = [EstAdmin]

    def get(self, request):
        il_y_a_7_jours = timezone.now() - timedelta(days=7)
        revenus = (
            Payment.objects.filter(statut=Payment.Statut.REUSSI).aggregate(t=Sum('montant'))['t'] or 0
        )
        vues = Contenu.objects.aggregate(t=Sum('vues'))['t'] or 0
        abonnes = sum(
            1
            for u in User.objects.exclude(plan=User.Plan.GRATUITE)
            if u.plan_effectif != User.Plan.GRATUITE
        )
        populaires = (
            Contenu.objects.filter(statut=Contenu.Statut.PUBLIE)
            .select_related('matiere')
            .order_by('-vues')[:5]
        )
        return Response(
            {
                'utilisateurs': User.objects.count(),
                'nouveaux_7_jours': User.objects.filter(date_joined__gte=il_y_a_7_jours).count(),
                'abonnes': abonnes,
                'revenus': revenus,
                'vues_totales': vues,
                'contenus_publies': Contenu.objects.filter(statut=Contenu.Statut.PUBLIE).count(),
                'contenus_en_attente': Contenu.objects.filter(
                    statut=Contenu.Statut.EN_ATTENTE
                ).count(),
                'populaires': [
                    {'id': c.id, 'titre': c.titre, 'matiere': c.matiere.nom, 'vues': c.vues}
                    for c in populaires
                ],
            }
        )


class AdminUserListView(APIView):
    permission_classes = [EstAdmin]

    def get(self, request):
        utilisateurs = User.objects.order_by('-date_joined')[:500]
        return Response(AdminUserSerializer(utilisateurs, many=True).data)


class AdminUserDetailView(APIView):
    permission_classes = [EstAdmin]

    def patch(self, request, pk):
        utilisateur = get_object_or_404(User, pk=pk)
        role = request.data.get('role')
        if role not in User.Role.values:
            return Response({'role': ['Rôle invalide.']}, status=400)
        if utilisateur.pk == request.user.pk:
            # Évite qu'un administrateur se retire lui-même l'accès
            return Response({'role': ['Tu ne peux pas changer ton propre rôle.']}, status=400)
        utilisateur.role = role
        utilisateur.save(update_fields=['role'])
        return Response(AdminUserSerializer(utilisateur).data)


class AdminPaymentListView(APIView):
    permission_classes = [EstAdmin]

    def get(self, request):
        paiements = Payment.objects.select_related('utilisateur')[:200]
        return Response(AdminPaymentSerializer(paiements, many=True).data)