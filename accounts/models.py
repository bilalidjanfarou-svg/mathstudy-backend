from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Étudiant'
        CREATOR = 'creator', 'Créateur'
        ADMIN = 'admin', 'Administrateur'

    class Plan(models.TextChoices):
        GRATUITE = 'gratuite', 'Gratuite'
        ETUDIANT = 'etudiant', 'Étudiant'
        PREMIUM = 'premium', 'Premium'

    email = models.EmailField(unique=True)
    nom_complet = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.GRATUITE)
    plan_expire_le = models.DateField(null=True, blank=True)
    universite = models.CharField(max_length=150, blank=True)
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def plan_effectif(self):
        """La formule réellement valable aujourd'hui.

        Sans date d'expiration (formule donnée à la main dans l'administration),
        la formule reste valable. Avec une date dépassée, on retombe sur Gratuite.
        """
        if (
            self.plan != self.Plan.GRATUITE
            and self.plan_expire_le
            and self.plan_expire_le < timezone.now().date()
        ):
            return self.Plan.GRATUITE
        return self.plan

    @property
    def plan_label_effectif(self):
        return self.Plan(self.plan_effectif).label

    def __str__(self):
        return self.email