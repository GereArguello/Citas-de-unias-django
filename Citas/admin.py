from django.contrib import admin
from .models import Cita
# Register your models here.

# class TaskAdmin(admin.ModelAdmin):
#     readonly_fields = ('created', )   MODO LECTURA


admin.site.register(Cita) #,TaskAdmin)

