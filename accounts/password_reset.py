import logging

from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import User

logger = logging.getLogger(__name__)

# Même réponse que le compte existe ou non : on ne révèle jamais qui est inscrit
MESSAGE = 'Si un compte existe avec cette adresse, un e-mail vient d’être envoyé.'


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'reset'

    def post(self, request):
        email = str(request.data.get('email') or '').strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first() if email else None

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            lien = f'{settings.FRONTEND_URL}/nouveau-mot-de-passe/{uid}/{token}'
            message = (
                'Bonjour,\n\n'
                'Tu as demandé à changer ton mot de passe LearnX. '
                'Ouvre ce lien (valable 1 heure) :\n\n'
                f'{lien}\n\n'
                'Si tu n’es pas à l’origine de cette demande, ignore ce message : '
                'ton mot de passe ne changera pas.\n\n'
                'L’équipe LearnX'
            )
            try:
                send_mail(
                    'LearnX : réinitialisation de ton mot de passe',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
            except Exception:
                logger.exception('Envoi de l’e-mail de réinitialisation impossible')

        return Response({'detail': MESSAGE})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'reset_confirm'

    def post(self, request):
        uid = str(request.data.get('uid') or '')
        token = str(request.data.get('token') or '')
        password = str(request.data.get('password') or '')

        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Lien invalide ou expiré. Refais une demande.'}, status=400
            )

        try:
            password_validation.validate_password(password, user)
        except ValidationError as e:
            return Response({'password': list(e.messages)}, status=400)

        user.set_password(password)  # enregistré chiffré, jamais en clair
        user.save(update_fields=['password'])
        return Response({'detail': 'Mot de passe modifié.'})