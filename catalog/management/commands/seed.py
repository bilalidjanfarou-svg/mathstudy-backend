from django.core.management.base import BaseCommand

from catalog.models import Chapitre, Contenu, Matiere

MATIERES = [
    # slug, nom, catégorie, premium, université, filière, niveau
    ('analyse-1', 'Analyse 1', 'maths', False, 'Université de Lomé', 'Mathématiques', 'Licence 1'),
    ('algebre-1', 'Algèbre 1', 'maths', True, 'Université de Lomé', 'Mathématiques', 'Licence 1'),
    ('probabilites-statistiques', 'Probabilités et Statistiques', 'maths', True, 'Université de Kara', 'Mathématiques', 'Licence 2'),
    ('algorithmique', 'Algorithmique', 'info', False, 'Université de Lomé', 'Informatique', 'Licence 1'),
    ('bases-de-donnees', 'Bases de données', 'info', True, 'Université de Kara', 'Informatique', 'Licence 2'),
    ('physique-generale', 'Physique générale', 'physique', False, 'Université de Lomé', 'Physique', 'Licence 1'),
    ('mecanique', 'Mécanique', 'physique', True, 'Université de Kara', 'Physique', 'Licence 2'),
    ('anglais-scientifique', 'Anglais scientifique', 'autres', False, 'Université de Lomé', 'Mathématiques', 'Licence 1'),
]

CHAPITRES_ANALYSE = [
    'Suites numériques',
    'Limites de fonctions',
    'Continuité',
    'Dérivabilité',
    'Intégrales',
]

CONTENUS_ANALYSE = [
    # type, titre, premium
    ('video', 'Cours vidéo : Limites', False),
    ('video', 'Cours vidéo : Continuité', False),
    ('video', 'Cours vidéo : Dérivées', True),
    ('pdf', 'Résumé : Suites', False),
    ('pdf', 'Résumé : Dérivées', False),
    ('pdf', 'Résumé : Intégrales', True),
    ('exercice', 'Série 1 : Suites', False),
    ('exercice', 'Série 2 : Dérivées', True),
    ('correction', 'Corrigé de la série 1', True),
    ('correction', 'Corrigé de la série 2', True),
    ('examen', 'Examen 2023 : Université de Lomé', True),
    ('examen', 'Examen 2022 : Université de Lomé', True),
]


class Command(BaseCommand):
    help = 'Charge des matières et contenus de départ (sans fichiers)'

    def handle(self, *args, **options):
        for slug, nom, cat, premium, univ, filiere, niveau in MATIERES:
            Matiere.objects.get_or_create(
                slug=slug,
                defaults={
                    'nom': nom,
                    'categorie': cat,
                    'premium': premium,
                    'universite': univ,
                    'filiere': filiere,
                    'niveau': niveau,
                },
            )

        analyse = Matiere.objects.get(slug='analyse-1')
        for i, titre in enumerate(CHAPITRES_ANALYSE, start=1):
            Chapitre.objects.get_or_create(matiere=analyse, ordre=i, defaults={'titre': titre})

        for type_, titre, premium in CONTENUS_ANALYSE:
            Contenu.objects.get_or_create(
                matiere=analyse,
                titre=titre,
                defaults={'type': type_, 'premium': premium, 'statut': 'publie'},
            )

        self.stdout.write(self.style.SUCCESS('Données de départ chargées.'))