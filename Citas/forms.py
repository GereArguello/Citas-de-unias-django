from django import forms
from .models import Cita
from datetime import date

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
                                          # ** recibe todos los parámetros con nombre como 'instance': cita
        self.fields['fecha'].input_formats = ['%Y-%m-%d']  #Le metemos el formato a 'fecha' para que al editar cita sea visible

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha.weekday() == 6:
            print(fecha)
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
    
