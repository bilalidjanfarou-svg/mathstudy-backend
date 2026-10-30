from django.urls import path

from .views import TicketDetailView, TicketListCreateView, TicketMessageCreateView

urlpatterns = [
    path('tickets/', TicketListCreateView.as_view()),
    path('tickets/<int:pk>/', TicketDetailView.as_view()),
    path('tickets/<int:pk>/messages/', TicketMessageCreateView.as_view()),
]