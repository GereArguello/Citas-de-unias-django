from django.urls import path
from . import views

urlpatterns = [
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/editar_turnos/', views.editar_turnos, name='editar_turnos')
]