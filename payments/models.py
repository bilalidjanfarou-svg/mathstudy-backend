import uuid

from django.conf import settings
from django.db import models


def nouvelle_reference():
    return 'MS-' + uuid.uuid4().hex[:12].upper()


class Payment(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        REUSSI = 'reussi', 'Réussi'
        ECHOUE = 'echoue', 'Échoué'

    class Moyen(models.TextChoices):
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CARTE = 'carte', 'Carte bancaire'

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='paiements'
    )
    plan = models.CharField(max_length=10)
    montant = models.PositiveIntegerField()  # en FCFA
    moyen = models.CharField(max_length=15, choices=Moyen.choices)
    telephone_fin = models.CharField(max_length=4, blank=True)  # on ne garde que les 4 derniers chiffres
    reference = models.CharField(max_length=20, unique=True, default=nouvelle_reference, editable=False)
    fournisseur = models.CharField(max_length=30, default='simulation')
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} : {self.utilisateur} : {self.montant} FCFA'