from django.urls import path

from .views import DashboardView, ProgressionView

urlpatterns = [
    path('progression/<int:contenu_id>/', ProgressionView.as_view()),
    path('dashboard/', DashboardView.as_view()),
]