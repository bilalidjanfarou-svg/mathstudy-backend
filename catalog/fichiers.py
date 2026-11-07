import mimetypes
import os
import re

from django.core import signing
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import Contenu

SEL = 'learnx-fichier'
DUREE = 2 * 60 * 60  # une adresse reste valable 2 heures


def url_fichier(request, contenu):
    """Adresse temporaire d'un fichier. À n'appeler qu'après avoir vérifié l'accès."""
    token = signing.dumps({'c': contenu.id}, salt=SEL)
    return request.build_absolute_uri(f'/api/fichiers/{token}/')


def lire(chemin, debut, longueur, bloc=1024 * 1024):
    with open(chemin, 'rb') as f:
        f.seek(debut)
        restant = longueur
        while restant > 0:
            donnees = f.read(min(bloc, restant))
            if not donnees:
                break
            restant -= len(donnees)
            yield donnees


@xframe_options_exempt  # permet d'afficher le PDF dans la page du front
def servir_fichier(request, token):
    try:
        donnees = signing.loads(token, salt=SEL, max_age=DUREE)
    except signing.BadSignature:  # adresse modifiée ou expirée
        raise Http404

    contenu = get_object_or_404(Contenu, pk=donnees.get('c'))
    if not contenu.fichier:
        raise Http404
    chemin = contenu.fichier.path
    if not os.path.isfile(chemin):
        raise Http404

    # Téléchargement : /api/fichiers/<adresse>/?telechargement=1
    if request.GET.get('telechargement'):
        return FileResponse(
            open(chemin, 'rb'), as_attachment=True, filename=os.path.basename(chemin)
        )

    taille = os.path.getsize(chemin)
    type_mime = mimetypes.guess_type(chemin)[0] or 'application/octet-stream'
    entetes = {
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'private, max-age=3600',
        'X-Content-Type-Options': 'nosniff',
    }

    # Lecture partielle : permet d'avancer dans une vidéo sans tout télécharger
    plage = re.match(r'bytes=(\d*)-(\d*)$', request.headers.get('Range', ''))
    if plage and (plage.group(1) or plage.group(2)):
        debut = int(plage.group(1)) if plage.group(1) else max(taille - int(plage.group(2)), 0)
        fin = int(plage.group(2)) if plage.group(1) and plage.group(2) else taille - 1
        fin = min(fin, taille - 1)
        if debut > fin:
            return HttpResponse(status=416, headers={'Content-Range': f'bytes */{taille}'})
        longueur = fin - debut + 1
        return StreamingHttpResponse(
            lire(chemin, debut, longueur),
            status=206,
            content_type=type_mime,
            headers={
                **entetes,
                'Content-Range': f'bytes {debut}-{fin}/{taille}',
                'Content-Length': str(longueur),
            },
        )

    return FileResponse(open(chemin, 'rb'), content_type=type_mime, headers=entetes)