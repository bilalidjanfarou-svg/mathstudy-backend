from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def api_root(request):
    return JsonResponse({'app': 'MathStudy API', 'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
]