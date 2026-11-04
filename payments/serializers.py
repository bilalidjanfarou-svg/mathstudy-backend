from rest_framework import serializers

from .models import Payment
from .plans import PLANS


class PaymentSerializer(serializers.ModelSerializer):
    plan_label = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'reference', 'plan', 'plan_label', 'montant',
            'moyen', 'statut', 'fournisseur', 'created_at',
        ]

    def get_plan_label(self, obj):
        return PLANS.get(obj.plan, {}).get('nom', obj.plan)