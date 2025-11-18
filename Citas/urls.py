from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='inicio'),
    
    path('registrarse/', views.registrarse, name='registrarse'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('iniciar_sesion/',views.iniciar_sesion, name= 'iniciar_sesion'),

    path('crear_cita/', views.crear_cita, name='crear_cita'),
    path('editar_cita/<int:id>/',views.editar_cita, name='editar_cita'),
    path('completar_cita/<int:id>', views.completar_cita, name="completar_cita"),
    path('eliminar/<int:id>/', views.eliminar_cita, name='eliminar_cita'),

    path('lista_citas/', views.lista_citas, name='lista_citas'),
    path('citas_completadas/', views.citas_completadas, name='citas_completadas')
]