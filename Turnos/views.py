from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from datetime import date
import calendar

from .forms import TurnosForm
from .models import DisponibilidadDia
from .utils import generar_calendario

from Citas.models import Cita


# Create your views here.
@login_required
def calendario(request):
    meses = [(1, "Enero"),(2, "Febrero"),(3, "Marzo"),(4, "Abril"),
    (5, "Mayo"),(6, "Junio"),(7, "Julio"),(8, "Agosto"),
    (9, "Septiembre"),(10, "Octubre"),(11, "Noviembre"),(12, "Diciembre"),]
    
    
    mes = request.GET.get("mes")
    año = request.GET.get("año")
    
    if not mes or not año: #Si aún no hay mes y año seleccionado, por defecto damos la fecha actual
        hoy = date.today()
        mes = hoy.month
        año = hoy.year
    else:
        mes = int(mes)
        año = int(año)

    año = max(2025,min(año,2040))
    
    inicio_mes = date(año, mes, 1)
    ultimo_dia = calendar.monthrange(año, mes)[1]
    fin_del_mes = date(año, mes, ultimo_dia)

    disponibilidad = DisponibilidadDia.objects.filter(fecha__range=(inicio_mes,fin_del_mes))
    disp_dia = {d.fecha: d.horarios for d in disponibilidad}

    citas_del_mes = Cita.objects.filter(fecha__range=(inicio_mes,fin_del_mes))

    hoy = date.today()

    ocupadas = {} #Creamos un diccionario que va a contener tuplas con la fecha y hora exacta de cada una
    
    for cita in citas_del_mes:
        ocupadas[(cita.fecha, cita.hora)] = True
        
    semanas = generar_calendario(año, mes)
    
    return render(request,'calendario/calendario.html',{'semanas': semanas, 'mes': mes, 'año': año, 'meses': meses, 'disponibilidad': disp_dia, 'ocupadas': ocupadas, 'hoy': hoy})

@login_required
def editar_turnos(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Solo un superusuario puede editar los turnos.")
    
    fecha = request.GET.get('fecha')
    instancia = DisponibilidadDia.objects.filter(fecha=fecha).first() if fecha else None

    # --- POST: guardar cambios o crear nueva disponibilidad ---
    if request.method == "POST":
        if instancia:  
            # Editar la instancia existente
            form = TurnosForm(request.POST, instance=instancia)
        else:
            # Crear una nueva instancia
            form = TurnosForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('calendario')

    # --- GET: mostrar formulario para editar o crear ---
    else:
        if instancia:  
            # Mostrar instancia existente
            form = TurnosForm(instance=instancia)
        elif fecha:  
            # Mostrar fecha predeterminada si no existe instancia
            form = TurnosForm(initial={'fecha': fecha})
        else:
            # No hay fecha seleccionada → formulario vacío
            form = TurnosForm()

    return render(request, 'calendario/editar_turnos.html', {
        'form': form
    })