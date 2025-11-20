from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from .forms import CitaForm
from .models import Cita

@login_required
def index(request):
    return render(request, 'inicio.html')

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
            form.save()
            return redirect('lista_citas')
    else:
        form = CitaForm()

    return render(request, 'crear_cita.html', {'form': form}) #'form' es la clave asociada al html

@login_required
def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)

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
    cita = get_object_or_404(Cita, id=id)
    cita.estado = True
    cita.save()
    return redirect('lista_citas')

@login_required
def eliminar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)

    if request.method == 'POST':
        cita.delete()
        messages.success(request,"✅ La cita fue eliminada con éxito.")
        if cita.estado == False:
            return redirect('lista_citas')
        else:
            return redirect('citas_completadas')

@login_required
def lista_citas(request):
    lista = Cita.objects.filter(estado=False).order_by('fecha') #Llamamos todo el contenido de la tabla

    return render(request,'lista_citas.html',{'lista': lista, 'tipo': 'pendientes'})

@login_required
def citas_completadas(request):
    lista = Cita.objects.filter(estado=True).order_by('-fecha')

    total_completadas = Cita.objects.filter(estado=True).aggregate(
        total=Sum('precio'))['total'] or 0
    
    return render(request,'lista_citas.html',{'lista': lista, 'tipo': 'completadas', 'total_completadas': total_completadas})