from django.db import models

# Create your models here.
class DisponibilidadDia(models.Model):
    fecha = models.DateField(unique=True)
    horarios = models.JSONField(default=list) # lista de strings: ["10:00", "14:30"]

    def __str__(self):
        return f"{self.fecha}: {', '.join(self.horarios)}"