from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'reservations', views.ReservationViewSet)

urlpatterns = [
    # path("", views.index, name="index")
    path('', include(router.urls)),
    path('userReservas/<int:user_id>/', views.user_reservations),
    path('usuarios/activos/', views.active_users),
]