from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Matiere(models.Model):
    class Categorie(models.TextChoices):
        MATHS = 'maths', 'Mathématiques'
        INFO = 'info', 'Informatique'
        PHYSIQUE = 'physique', 'Physique'
        AUTRES = 'autres', 'Autres'

    nom = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    categorie = models.CharField(max_length=10, choices=Categorie.choices, default=Categorie.MATHS)
    universite = models.CharField(max_length=150, blank=True)
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=30, blank=True)
    premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'matière'
        verbose_name_plural = 'matières'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def nb_ressources(self):
        return self.contenus.filter(statut=Contenu.Statut.PUBLIE).count()

    def __str__(self):
        return self.nom


class Chapitre(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='chapitres')
    titre = models.CharField(max_length=200)
    ordre = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f'{self.matiere.nom} : {self.ordre}. {self.titre}'


class Contenu(models.Model):
    class Type(models.TextChoices):
        VIDEO = 'video', 'Vidéo'
        PDF = 'pdf', 'Résumé PDF'
        EXERCICE = 'exercice', 'Exercices'
        CORRECTION = 'correction', 'Correction'
        EXAMEN = 'examen', 'Examen'

    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        PUBLIE = 'publie', 'Publié'
        REFUSE = 'refuse', 'Refusé'

    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='contenus')
    chapitre = models.ForeignKey(
        Chapitre, on_delete=models.SET_NULL, null=True, blank=True, related_name='contenus'
    )
    type = models.CharField(max_length=12, choices=Type.choices)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='contenus/%Y/%m/', blank=True)
    duree_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    pages = models.PositiveSmallIntegerField(null=True, blank=True)
    premium = models.BooleanField(default=False)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE)
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contenus_crees',
    )
    vues = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.titre