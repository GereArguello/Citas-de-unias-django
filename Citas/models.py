from django.db import models
from django.contrib.auth.models import User
#con esto podemos asignar la cita a un usuario 
import datetime

class Cita (models.Model):      #Creamos una tabla
    SERVICIOS = [
        ('Manicura', 'Manicura'), #Lista de tuplas, (como lo ves, como lo ven)
        ('Pedicura', 'Pedicura'),
        ('Semipermanente', 'Semipermanente'),
    ]

    HORARIOS = [
        (datetime.time(10, 0), '10:00'),
        (datetime.time(12, 0), '12:00'),
        (datetime.time(14, 0), '14:00'),
        (datetime.time(16, 0), '16:00'),
    ]

    nombre_clienta = models.CharField(max_length=100)
    servicio = models.CharField(max_length=100, choices=SERVICIOS)
    precio = models.IntegerField(null=True)
    fecha = models.DateField()
    hora = models.TimeField(choices=HORARIOS)
    comentario = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank= True)

    def __str__(self): #Forma de representarlo como administrador
        return f"{self.nombre_clienta} - {self.servicio} ({self.fecha.strftime('%d/%m')} - {self.hora.strftime('%H:%M')})"
