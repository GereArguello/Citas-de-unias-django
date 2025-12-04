from django import forms
from .models import Cita, Profile
from datetime import date
from django.contrib.auth.models import User
import re

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['nombre_clienta', 'servicio','precio', 'fecha', 'hora', 'comentario']
        widgets = {
            'nombre_clienta': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(format='%Y-%m-%d',attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,            # textarea más chico
                'placeholder': 'Escribe un comentario (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # * recibe todos los argumentos posicionales como request.POST
                                          # ** recibe todos los parámetros con nombre como {'instance': cita}
        self.fields['fecha'].input_formats = ['%Y-%m-%d']  #Le metemos el formato a 'fecha' para que al editar cita sea visible

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha.weekday() == 6:
            raise forms.ValidationError("No se atiende los domingos.")
        return fecha
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

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