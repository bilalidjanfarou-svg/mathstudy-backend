from django.conf import settings
from django.db import models


class Progression(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progressions'
    )
    contenu = models.ForeignKey(
        'catalog.Contenu', on_delete=models.CASCADE, related_name='progressions'
    )
    termine = models.BooleanField(default=False)
    derniere_vue = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('utilisateur', 'contenu')
        ordering = ['-derniere_vue']

    def __str__(self):
        return f'{self.utilisateur} : {self.contenu} ({"terminé" if self.termine else "en cours"})'