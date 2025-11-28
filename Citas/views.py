from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import CitaForm
from .models import Cita
from .utils import semana_actual, mes_actual, citas_para_usuario, generar_calendario
from datetime import date
import calendar

@login_required
def index(request):
    return render(request, 'inicio.html', {'user': request.user})

def registrarse(request):
    if request.method == 'GET':
        return render(request, 'registrarse.html', {
            'form': UserCreationForm()
        })

    form = UserCreationForm(request.POST)
    
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('inicio')

    return render(request, 'registrarse.html', {
        'form': form,
        'error': 'Corrige los errores del formulario.'
    })

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')

def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'iniciar_sesion.html', {
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request, 
                            username=request.POST.get('username'), 
                            password=request.POST.get('password'))
        if user is None:
            return render(request, 'iniciar_sesion.html', {
                'form': AuthenticationForm(), 'error': 'El usuario o contraseña son incorrectos.'
            })
        else:
            login(request,user)
            return redirect('inicio')

@login_required
def crear_cita(request):
    if request.method == "POST": #El método es el mismo que HTML
        form = CitaForm(request.POST) #Variable que contiene el formulario
        if form.is_valid():
            cita = form.save(commit=False) #Crear cita sin guardar
            cita.user = request.user #Asignar dueño
            cita.save()
            return redirect('lista_citas')
    else:
        form = CitaForm()

    return render(request, 'crear_cita.html', {'form': form}) #'form' es la clave asociada al html

@login_required
def editar_cita(request, id):
    if request.user.is_superuser:
        cita = get_object_or_404(Cita, id=id)
    else:
        cita = get_object_or_404(Cita, id=id, user=request.user)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita) #instance para editar un objeto existente
        if form.is_valid():
            form.save()
            return redirect('lista_citas')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'editar_cita.html', {'form': form})

@login_required
@require_POST
def completar_cita(request, id):
    if request.user.is_superuser:
        cita = get_object_or_404(Cita, id=id)
        cita.estado = True
        cita.save()
    return redirect('lista_citas')

@login_required
def eliminar_cita(request, id):
    if request.user.is_superuser:
        cita = get_object_or_404(Cita, id=id)
    else:
        cita = get_object_or_404(Cita, id=id, user=request.user)

    if request.method == 'POST':
        estado_original = cita.estado
        cita.delete()
        messages.success(request,"✅ La cita fue eliminada con éxito.")
        if not estado_original:
            return redirect('lista_citas')
        else:
            return redirect('citas_completadas')

@login_required
def lista_citas(request):
    lista = citas_para_usuario(request.user).filter(estado=False).order_by('fecha') #Llamamos todo el contenido de la tabla

    return render(request,'lista_citas.html',{'lista': lista})

@login_required
def citas_completadas(request):
    lista = citas_para_usuario(request.user).filter(estado=True).order_by('-fecha')

    total_completadas = lista.aggregate(
        total=Sum('precio'))['total'] or 0
    
    return render(request,'lista_completadas.html',{'lista': lista, 'total': total_completadas})

@login_required
def filtrar_semana(request):
    inicio, fin = semana_actual()

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio,fin)).order_by('-fecha')

    total_semana = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(request, 'lista_completadas.html',{
        'lista': lista, 'total':total_semana, 'rango':(inicio, fin)
    })

@login_required
def filtrar_mes(request):
    inicio, fin = mes_actual()

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio,fin)).order_by('-fecha')
    
    total_mes = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(request, 'lista_completadas.html',{
        'lista': lista, 'total':total_mes, 'rango':(inicio, fin)
    })

@login_required
def filtrar_personalizado(request):
    inicio_str = request.GET.get('inicio')
    fin_str = request.GET.get('fin')

    # Si no hay fechas, redirige
    if not (inicio_str and fin_str):
        return redirect('citas_completadas')

    # Convertir las fechas válidas
    inicio = date.fromisoformat(inicio_str)
    fin = date.fromisoformat(fin_str)

    rango = (inicio, fin)

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio, fin)
    ).order_by('-fecha')

    total_personalizado = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(
        request,
        'lista_completadas.html',
        {
            'lista': lista,
            'total': total_personalizado,
            'rango': rango
        }
    )
    
@login_required
def calendario(request):
    meses = [(1, "Enero"),(2, "Febrero"),(3, "Marzo"),(4, "Abril"),
    (5, "Mayo"),(6, "Junio"),(7, "Julio"),(8, "Agosto"),
    (9, "Septiembre"),(10, "Octubre"),(11, "Noviembre"),(12, "Diciembre"),]
    
    opciones = Cita.HORARIOS
    
    mes = request.GET.get("mes")
    año = request.GET.get("año")
    
    if not mes or not año:
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
    citas_del_mes = Cita.objects.filter(fecha__range=(inicio_mes,fin_del_mes))

    ocupadas = {}
    
    for cita in citas_del_mes:
        ocupadas[(cita.fecha, cita.hora)] = True
        
    semanas = generar_calendario(año, mes)
    
    return render(request,'calendario.html',{'semanas': semanas, 'mes': mes, 'año': año, 'meses': meses, 'opciones': opciones, 'ocupadas': ocupadas})