from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Statut(models.TextChoices):
        OUVERT = 'ouvert', 'Ouvert'
        REPONDU = 'repondu', 'Répondu'
        RESOLU = 'resolu', 'Résolu'

    class Categorie(models.TextChoices):
        COMPTE = 'compte', 'Mon compte'
        CONTENU = 'contenu', 'Un cours ou un contenu'
        PAIEMENT = 'paiement', 'Paiement et abonnement'
        TECHNIQUE = 'technique', 'Problème technique'
        AUTRE = 'autre', 'Autre'

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets'
    )
    sujet = models.CharField(max_length=200)
    categorie = models.CharField(max_length=10, choices=Categorie.choices, default=Categorie.AUTRE)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.OUVERT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.sujet


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texte = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.ticket_id} : {self.texte[:40]}'