from django.db import models
from django.contrib.auth.models import User
#con esto podemos asignar la cita a un usuario 
import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

class Cita (models.Model):      #Creamos una tabla
    SERVICIOS = [
        ('Manicura', 'Manicura'), #Lista de tuplas, (como lo ves, como lo ven)
        ('Pedicura', 'Pedicura'),
        ('Semipermanente', 'Semipermanente'),
    ]



    nombre_clienta = models.CharField(max_length=100)
    servicio = models.CharField(max_length=100, choices=SERVICIOS)
    precio = models.IntegerField(null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    comentario = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, blank= True)

    def __str__(self): #Forma de representarlo como administrador
        return f"{self.nombre_clienta} - {self.servicio} ({self.fecha.strftime('%d/%m')} - {self.hora.strftime('%H:%M')})"
    
class DisponibilidadDia(models.Model):
    fecha = models.DateField(unique=True)
    horarios = models.JSONField(default=list) # lista de strings: ["10:00", "14:30"]

    def __str__(self):
        return f"{self.fecha}: {', '.join(self.horarios)}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def crear_o_actualizar_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)

