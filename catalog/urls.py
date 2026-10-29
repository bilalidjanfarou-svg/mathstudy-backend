from django.urls import path

from .views import ContenuDetailView, MatiereDetailView, MatiereListView

urlpatterns = [
    path('matieres/', MatiereListView.as_view()),
    path('matieres/<slug:slug>/', MatiereDetailView.as_view()),
    path('contenus/<int:pk>/', ContenuDetailView.as_view()),
]