from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.static import serve


def api_root(request):
    return JsonResponse({'app': 'MathStudy API', 'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('catalog.urls')),
]

if settings.DEBUG:
    # Servir les fichiers envoyés (vidéos, PDF) en développement,
    # en autorisant leur affichage dans le front React
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            xframe_options_exempt(serve),
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]