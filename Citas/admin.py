from django.contrib import admin
from .models import Cita, Profile, DisponibilidadDia
# Register your models here.

# class TaskAdmin(admin.ModelAdmin):
#     readonly_fields = ('created', )   MODO LECTURA


admin.site.register(Cita) #,TaskAdmin)
admin.site.register(Profile) #,TaskAdmin)
admin.site.register(DisponibilidadDia) #,TaskAdmin)