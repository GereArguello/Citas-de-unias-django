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

        # 1) Si viene por POST (cuando enviás el form para guardar)
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

        # 4) Con la fecha ya resuelta, cargamos los horarios
        if fecha:
            try:
                disponibilidad = DisponibilidadDia.objects.get(fecha=fecha)
                horarios = [(h, h) for h in disponibilidad.horarios]

                # INCLUIMOS LA LÍNEA CLAVE PARA QUE SE RENDERICE EL SELECT
                self.fields['hora'].choices = horarios
                self.fields['hora'].widget.choices = horarios   # ← NUEVO FIX

                # Incluir la hora actual al editar
                if self.instance and self.instance.hora:
                    hora_actual = self.instance.hora.strftime("%H:%M")
                    if (hora_actual, hora_actual) not in horarios:
                        horarios.append((hora_actual, hora_actual))

                print(">>> FECHA RESUELTA EN FORM:", fecha)
                print(">>> DISPONIBILIDAD:", disponibilidad.horarios)

            except DisponibilidadDia.DoesNotExist:
                self.fields['hora'].choices = [("", "No hay horarios disponibles este día")]
                self.fields['hora'].widget.choices = self.fields['hora'].choices
        else:
            self.fields['hora'].choices = [("", "Seleccione una fecha primero")]
            self.fields['hora'].widget.choices = self.fields['hora'].choices

        self.fields['fecha'].input_formats = ['%Y-%m-%d']
    
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
        
        if precio < 0:
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