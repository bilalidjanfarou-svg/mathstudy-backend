import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Crée le compte administrateur à partir de ADMIN_EMAIL et ADMIN_PASSWORD'

    def handle(self, *args, **options):
        email = os.environ.get('ADMIN_EMAIL', '').strip().lower()
        password = os.environ.get('ADMIN_PASSWORD', '')

        if not email or not password:
            self.stdout.write('ADMIN_EMAIL ou ADMIN_PASSWORD manquant : rien à faire.')
            return

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write('Le compte administrateur existe déjà.')
            return

        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            role='admin',
            nom_complet='Administrateur',
        )
        self.stdout.write(self.style.SUCCESS('Compte administrateur créé.'))