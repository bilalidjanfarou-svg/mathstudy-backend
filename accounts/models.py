from django.contrib.auth.models import AbstractUser
from django.db import models


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
    universite = models.CharField(max_length=150, blank=True)
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email