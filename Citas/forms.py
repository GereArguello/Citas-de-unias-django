from django import forms
from .models import Cita, Profile, DisponibilidadDia
from datetime import date, datetime
from django.contrib.auth.models import User
import re


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora', 'nombre_clienta', 'servicio', 'precio', 'comentario']
        widgets = {
            'nombre_clienta': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'onchange': 'cambiar_fecha(this.value)'
                }
            ),
            'hora': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe un comentario (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        fecha = kwargs.pop("fecha", None)
        super().__init__(*args, **kwargs)


        # 1) Si la fecha viene desde el formulario (GET por onchange o POST al guardar)
        if self.data.get('fecha'):
            fecha_str = self.data.get('fecha')

            if isinstance(fecha_str, date):
                fecha = fecha_str
            else:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                except ValueError:
                    fecha = None

        # 2) Si estás editando una cita existente
        if not fecha and self.instance and self.instance.fecha:
            fecha = self.instance.fecha

        # 3) Si viene por GET como initial
        if not fecha and self.initial.get('fecha'):
            fecha_str = self.initial.get('fecha')
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                fecha = None
        
        # Forzar fecha en el input HTML SOLO si es válida
        if fecha:
            # Si viene como string, convertirla
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                except:
                    fecha = None

        if fecha:
            fecha_str = fecha.strftime("%Y-%m-%d")
            self.fields['fecha'].initial = fecha_str
            self.fields['fecha'].widget.attrs['value'] = fecha_str

        # 4) Con la fecha ya resuelta, cargamos los horarios
        if fecha:
            try:
                disponibilidad = DisponibilidadDia.objects.get(fecha=fecha)
                
                # 1) Lista original de horarios disponibles en ese día
                horarios_disponibles = list(disponibilidad.horarios)
                        
                # Si hay disponibilidad registrada, pero VACÍA
                if not horarios_disponibles:
                    self.fields['hora'].choices = [("", "No hay horarios disponibles este día")]
                    self.fields['hora'].widget.choices = self.fields['hora'].choices
                    return  

                # 2) Obtener horarios ya ocupados por citas reales
                ocupados_qs = Cita.objects.filter(fecha=fecha).values_list("hora", flat=True)

                # Convertimos horas datetime.time → "HH:MM"
                ocupados = {h.strftime("%H:%M") for h in ocupados_qs}

                # 3) Filtramos dejando SOLO horarios libres
                horarios_filtrados = [
                    h for h in horarios_disponibles if h not in ocupados
                ]

                # 4) Si estamos editando, permitimos que aparezca la hora actual aunque esté ocupada
                if self.instance and self.instance.hora:
                    hora_actual = self.instance.hora.strftime("%H:%M")
                    if hora_actual not in horarios_filtrados:
                        horarios_filtrados.append(hora_actual)

                # Convertimos a choices
                horarios = [(h, h) for h in sorted(horarios_filtrados)]

                # Renderizamos el select
                self.fields['hora'].choices = horarios
                self.fields['hora'].widget.choices = horarios

            except DisponibilidadDia.DoesNotExist:
                self.fields['hora'].choices = [("", "No hay horarios disponibles este día")]
                self.fields['hora'].widget.choices = self.fields['hora'].choices
        else: 
            self.fields['hora'].choices = [("", "Seleccione una fecha primero")] 
            self.fields['hora'].widget.choices = self.fields['hora'].choices

    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        precio = cleaned_data.get('precio')

        if fecha and fecha < date.today():
            raise forms.ValidationError("Ingrese una fecha válida")
        
        if fecha and hora:
            # Buscamos otras citas que tengan la misma cita y hora
            qs = Cita.objects.filter(fecha=fecha, hora=hora)
            
            #Si la instancia tiene pk, significa que estamos editando una cita existente.
            if self.instance and self.instance.pk:   #pk: primary key
                qs = qs.exclude(pk=self.instance.pk)  # Excluimos la cita actual para no bloquear la edición

            if qs.exists(): #al excluirla, evitamos que este paso se cumpla
                raise forms.ValidationError("Ese turno ya está ocupado.")
        
        if precio is not None and precio < 0:
            raise forms.ValidationError("Ingrese un precio válido")

        return cleaned_data
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'ejemplo@mail.com'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telefono']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'+52 xxx xxx xxxx'}),
        }
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']

        if not telefono:
            telefono = ""
            return telefono
        
        telefono = telefono.strip()

        telefono_num = re.sub(r"\D","", telefono) #Dejar solo números

        if len(telefono_num) < 8 or len(telefono_num) > 14 :
            raise forms.ValidationError("Teléfono inválido")
        return telefono_num
    
class TurnosForm(forms.ModelForm):

    horario1 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario2 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario3 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario4 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario5 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DisponibilidadDia
        fields = ['fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class':'form-control','type': 'date','onchange': 'cambiar_fecha(this.value)'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ajustar label dinámicamente
        for i in range(1, 6):
            self.fields[f"horario{i}"].label = f"Horario {i}"

        if self.instance and self.instance.horarios:
            horarios = self.instance.horarios  # lista ejemplo ["10:00", "11:00"]

            # Prellenar por índice
            for i, hora in enumerate(horarios):
                if i < 5:
                    self.fields[f"horario{i+1}"].initial = hora    

    def clean(self):
        cleaned = super().clean()

        horarios = []
        for i in range(1, 6):
            valor = cleaned.get(f"horario{i}")
            if valor:
                horarios.append(valor.strftime("%H:%M"))

        cleaned["horarios"] = horarios
        return cleaned
    
    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.horarios = self.cleaned_data["horarios"]
        if commit:
            instancia.save()
        return instancia
