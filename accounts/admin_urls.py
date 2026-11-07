from django.urls import path

from .admin_views import (
    AdminPaymentListView,
    AdminStatsView,
    AdminUserDetailView,
    AdminUserListView,
)

urlpatterns = [
    path('admin/stats/', AdminStatsView.as_view()),
    path('admin/utilisateurs/', AdminUserListView.as_view()),
    path('admin/utilisateurs/<int:pk>/', AdminUserDetailView.as_view()),
    path('admin/paiements/', AdminPaymentListView.as_view()),
]