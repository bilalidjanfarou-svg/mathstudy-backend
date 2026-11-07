from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from catalog.fichiers import servir_fichier


def api_root(request):
    return JsonResponse({'app': 'LearnX API', 'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/fichiers/<str:token>/', servir_fichier),
    path('api/auth/', include('accounts.urls')),
    path('api/support/', include('support.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/', include('progress.urls')),
    path('api/', include('accounts.admin_urls')),
    path('api/', include('catalog.creator_urls')),
    path('api/', include('catalog.urls')),
]