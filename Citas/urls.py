from django.urls import path
from . import views

urlpatterns = [
    
    path('crear_cita/', views.crear_cita, name='crear_cita'),
    path('editar_cita/<int:id>/',views.editar_cita, name='editar_cita'),
    path('completar_cita/<int:id>', views.completar_cita, name="completar_cita"),
    path('eliminar/<int:id>/', views.eliminar_cita, name='eliminar_cita'),

    path('lista_citas/', views.lista_citas, name='lista_citas'),
    path('citas_completadas/', views.citas_completadas, name='citas_completadas'),
    path('citas_completadas/semana', views.filtrar_semana, name='lista_semana'),
    path('citas_completadas/mes', views.filtrar_mes, name= 'lista_mes'),
    path('citas_completadas/personalizado/', views.filtrar_personalizado, name='lista_personalizada'),
]