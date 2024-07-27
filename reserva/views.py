from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from .models import User, Room, Reservation
from .serializers import UserSerializer, RoomSerializer, ReservationSerializer

def index(request):
    return HttpResponse("hola de nuevo")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

@api_view(["GET"])
def user_reservations(request, user_id):
    """
    Obtiene todas las reservas de un usuario específico.
    """
    try:
        reservations = Reservation.objects.filter(user_id=user_id)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
@api_view(["GET"])
def active_users(request):
    """
    Obtiene todos los usuarios activos.
    """
    try:
        users = User.objects.filter(is_active=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
