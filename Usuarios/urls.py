from django.urls import path
from . import views

urlpatterns = [
    path('registrarse/', views.registrarse, name='registrarse'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('iniciar_sesion/',views.iniciar_sesion, name= 'iniciar_sesion'),

    path('mi_perfil/',views.mi_perfil, name= 'mi_perfil'),
    path('mi_perfil/editar_perfil/', views.editar_perfil, name= 'editar_perfil'),
    path('mi_perfil/cambiar_pass/', views.cambiar_pass, name= 'cambiar_pass'),
    path('mi_perfil/eliminar_perfil/', views.eliminar_perfil, name= 'eliminar_perfil'),
]