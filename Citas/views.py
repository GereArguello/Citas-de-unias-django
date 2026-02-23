from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import CitaForm
from .models import Cita
from .utils import semana_actual, mes_actual, citas_para_usuario
from datetime import date
from django.http import HttpResponseForbidden

@login_required
def index(request):
    return render(request, 'inicio.html', {'user': request.user})


@login_required
def crear_cita(request):

    fecha_inicial = request.GET.get("fecha")

    if request.method == "POST":
        
        form = CitaForm(request.POST, fecha=request.POST.get("fecha"))

        if request.user.is_superuser:
            total_agenda = 0
        else:
            total_agenda = Cita.objects.filter(estado=False, user=request.user).count()

        if total_agenda >= 3:
            error = "No puedes agendar más de 3 citas"
            return render(request, "citas/crear_cita.html",{'form': form,'error': error})

        if form.is_valid():
            cita = form.save(commit=False)
            cita.user = request.user
            cita.save()
            return redirect("lista_citas")
    else:
        # GET con o sin fecha
        form = CitaForm(initial={"fecha": fecha_inicial}, fecha=fecha_inicial)

    return render(request, "citas/crear_cita.html", {"form": form})

@login_required
def editar_cita(request, id):
    if request.user.is_superuser: #El super usuario puede acceder a todas las citas
        cita = get_object_or_404(Cita, id=id)
    else:
        cita = get_object_or_404(Cita, id=id, user=request.user) #Un usuario común solo puede editar las suyas

    fecha_inicial = request.GET.get("fecha")

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita, fecha=request.POST.get("fecha")) #instance para editar un objeto existente
        if form.is_valid():
            if not request.user.is_superuser:
                cita.user = request.user  # se asegura de que la cita siga siendo suya
            form.save()
            return redirect('lista_citas')
    else:
        form = CitaForm(instance=cita,initial={"fecha": fecha_inicial}, fecha= fecha_inicial)

    return render(request, 'citas/editar_cita.html', {'form': form})

@login_required
@require_POST #Exige que se confirme vía POST, evitando así una url como /completar_cita/12
def completar_cita(request, id):
    if request.user.is_superuser:
        cita = get_object_or_404(Cita, id=id)
        cita.estado = True
        cita.save()
        messages.success(request, "Cita completada con éxito.")
    return redirect('lista_citas')

@login_required
@require_POST
def eliminar_cita(request, id):
    if request.user.is_superuser:
        cita = get_object_or_404(Cita, id=id)
    else:
        cita = get_object_or_404(Cita, id=id, user=request.user)

    if request.method == 'POST':
        estado_original = cita.estado
        cita.delete()
        messages.success(request,"✅ La cita fue eliminada con éxito.")
        if not estado_original:  #Si el estado no era 'completada', nos redirecciona a lista_citas
            return redirect('lista_citas') #Con esto nos aseguramos que el usuario se redireccione a la página en la que estaba
        else:
            return redirect('citas_completadas')

@login_required
def lista_citas(request):
    lista = citas_para_usuario(request.user).filter(estado=False).order_by('fecha') #Llamamos todo el contenido de la tabla

    return render(request,'citas/lista_citas.html',{'lista': lista})

@login_required
def citas_completadas(request):
    lista = citas_para_usuario(request.user).filter(estado=True).order_by('-fecha')[:20]

    lista_hoy = citas_para_usuario(request.user).filter(estado=True, fecha=date.today()).order_by('-fecha')

    total_completadas = lista_hoy.aggregate(total=Sum('precio'))['total'] or 0 #Si la clave total fuera None, devuelve 0
    
    return render(request,'citas/lista_completadas.html',{'lista': lista, 'total': total_completadas})

@login_required
def filtrar_semana(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("No tenés permiso para acceder a esta sección.")
    
    inicio, fin = semana_actual() #Desempaquetamos el rango de la semana

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio,fin)).order_by('-fecha')

    total_semana = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(request, 'citas/lista_completadas.html',{
        'lista': lista, 'total':total_semana, 'rango':(inicio, fin)
    })

@login_required
def filtrar_mes(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("No tenés permiso para acceder a esta sección.")
    
    inicio, fin = mes_actual() #Desempaquetamos el rango del mes

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio,fin)).order_by('-fecha')
    
    total_mes = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(request, 'citas/lista_completadas.html',{
        'lista': lista, 'total':total_mes, 'rango':(inicio, fin)
    })

@login_required
def filtrar_personalizado(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("No tenés permiso para acceder a esta sección.")
    
    inicio_str = request.GET.get('inicio') #Recibimos del formulario ambas fechas
    fin_str = request.GET.get('fin')

    # Si no hay fechas, redirige
    if not (inicio_str and fin_str):
        return redirect('citas_completadas')

    try:
        inicio = date.fromisoformat(inicio_str)
        fin = date.fromisoformat(fin_str)
    except ValueError:
        messages.error(request, "Formato de fecha inválido.")
        return redirect('citas_completadas')

    # Validar orden
    if fin < inicio:
        error = "La fecha final no puede ser menor a la inicial."
        total = 0
        return render(request, "citas/lista_completadas.html", {"error": error, 'total': total})

    if (fin - inicio).days > 90:
        error = "El rango máximo permitido es de 90 días."
        total = 0
        return render(request, "citas/lista_completadas.html", {"error": error, 'total': total})

    rango = (inicio, fin)

    lista = citas_para_usuario(request.user).filter(
        estado=True,
        fecha__range=(inicio, fin)
    ).order_by('-fecha')

    total_personalizado = lista.aggregate(total=Sum('precio'))['total'] or 0

    return render(
        request,
        'citas/lista_completadas.html',
        {
            'lista': lista,
            'total': total_personalizado,
            'rango': rango
        }
    )
    
