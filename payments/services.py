from datetime import timedelta

from django.utils import timezone

from .plans import DUREE_JOURS


def activer_abonnement(user, plan):
    """Active la formule pour 30 jours. Un renouvellement de la même formule prolonge la date."""
    aujourdhui = timezone.now().date()
    debut = aujourdhui
    if user.plan == plan and user.plan_expire_le and user.plan_expire_le > aujourdhui:
        debut = user.plan_expire_le

    user.plan = plan
    user.plan_expire_le = debut + timedelta(days=DUREE_JOURS)
    user.save(update_fields=['plan', 'plan_expire_le'])