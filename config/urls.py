from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({'app': 'MathStudy API', 'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/', include('catalog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)