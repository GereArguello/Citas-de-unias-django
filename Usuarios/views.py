from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages

from Citas.models import Cita

from .forms import UserForm, ProfileForm
from .models import Profile
# Create your views here.
@login_required
def mi_perfil(request):
    usuario = request.user
    profile, created = Profile.objects.get_or_create(user=usuario)
    total_citas = Cita.objects.filter(estado=True, user=request.user).count()
    return render(request,'perfil/mi_perfil.html',{'usuario': usuario, 'profile': profile, 'total_citas': total_citas})

@login_required
def editar_perfil(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserForm(request.POST, instance= user)
        profile_form = ProfileForm(request.POST, instance= profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect ('mi_perfil')
    else:
        user_form = UserForm(instance= user)
        profile_form = ProfileForm(instance= profile)

    formularios = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request,'perfil/editar_perfil.html',formularios)

@login_required
def cambiar_pass(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Contraseña cambiada correctamente")
            return redirect('mi_perfil')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request,'perfil/cambiar_pass.html',{'form': form})

@login_required
def eliminar_perfil(request):

    #Bloquear al superusuario ANTES de procesar el POST
    if request.user.is_superuser:
        return render(request, 'perfil/eliminar_perfil.html', {
            "error": "Un superusuario no puede eliminar su propia cuenta."
        })

    if request.method == "POST":
        texto = request.POST.get("confirmacion", "")
        if texto == "CONFIRMAR":
            user = request.user       
            logout(request)
            user.delete()
            return redirect('registrarse')
        
        return render (request, 'perfil/eliminar_perfil.html',{
            "error": "Debes escribir la palabra CONFIRMAR exactamente"
        })
    return render(request,'perfil/eliminar_perfil.html')

def registrarse(request):
    if request.method == 'GET': #Si el request pide datos:
        return render(request, 'auth/registrarse.html', {
            'form': UserCreationForm()
        })

    form = UserCreationForm(request.POST)
    
    if form.is_valid(): #si el formulario es válido, ENVÍA datos
        user = form.save()
        login(request, user)
        return redirect('inicio')

    return render(request, 'auth/registrarse.html', {
        'form': form, 
    })

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')

def iniciar_sesion(request):
    if request.method == 'GET': #Si el request pide datos:
        return render(request, 'auth/iniciar_sesion.html', {
        })
    else: #Al ser POST, autenticamos datos del formulario
        user = authenticate(request, 
                            username=request.POST.get('username'), 
                            password=request.POST.get('password'))
        if user is None: #Si no hay usuario que coincida, re-enviamos la página pero esta vez con la clave 'error'
            return render(request, 'auth/iniciar_sesion.html', {
                'error': 'El usuario o contraseña son incorrectos.'
            })
        else:
            login(request,user)
            return redirect('inicio')
