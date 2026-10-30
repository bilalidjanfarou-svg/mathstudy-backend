from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket, TicketMessage
from .serializers import (
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
)


def ticket_pour(user, pk):
    """Un étudiant ne voit que ses demandes. Un administrateur voit tout."""
    ticket = get_object_or_404(
        Ticket.objects.select_related('auteur').prefetch_related('messages__auteur'), pk=pk
    )
    if user.role != 'admin' and ticket.auteur_id != user.id:
        raise Http404
    return ticket


class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.select_related('auteur')
        if request.user.role != 'admin':
            tickets = tickets.filter(auteur=request.user)
        return Response(TicketListSerializer(tickets, many=True).data)

    def post(self, request):
        s = TicketCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        ticket = Ticket.objects.create(
            auteur=request.user, sujet=d['sujet'], categorie=d['categorie']
        )
        TicketMessage.objects.create(ticket=ticket, auteur=request.user, texte=d['texte'])
        return Response(TicketDetailSerializer(ticket_pour(request.user, ticket.pk)).data, status=201)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        return Response(TicketDetailSerializer(ticket_pour(request.user, pk)).data)

    def patch(self, request, pk):
        ticket = ticket_pour(request.user, pk)
        statut = request.data.get('statut')
        autorises = ['resolu'] if request.user.role != 'admin' else ['ouvert', 'repondu', 'resolu']
        if statut not in autorises:
            return Response({'statut': ['Changement non autorisé.']}, status=400)
        ticket.statut = statut
        ticket.save()
        return Response(TicketDetailSerializer(ticket_pour(request.user, pk)).data)


class TicketMessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = ticket_pour(request.user, pk)
        texte = (request.data.get('texte') or '').strip()
        if not texte:
            return Response({'texte': ['Écris un message.']}, status=400)
        if len(texte) > 5000:
            return Response({'texte': ['Message trop long (5000 caractères maximum).']}, status=400)

        TicketMessage.objects.create(ticket=ticket, auteur=request.user, texte=texte)
        ticket.statut = Ticket.Statut.REPONDU if request.user.role == 'admin' else Ticket.Statut.OUVERT
        ticket.save()
        return Response(TicketDetailSerializer(ticket_pour(request.user, pk)).data, status=201)