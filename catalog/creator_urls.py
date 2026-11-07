from django.urls import path

from .creator_views import (
    AdminContenuDetailView,
    AdminContenuListView,
    CreatorContenuListCreateView,
)

urlpatterns = [
    path('creator/contenus/', CreatorContenuListCreateView.as_view()),
    path('admin/contenus/', AdminContenuListView.as_view()),
    path('admin/contenus/<int:pk>/', AdminContenuDetailView.as_view()),
]