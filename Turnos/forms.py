from django import forms
from .models import DisponibilidadDia

class TurnosForm(forms.ModelForm):

    horario1 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario2 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario3 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario4 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario5 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    horario6 = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DisponibilidadDia
        fields = ['fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class':'form-control','type': 'date','onchange': 'cambiar_fecha(this.value)'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ajustar label dinámicamente
        for i in range(1, 7):
            self.fields[f"horario{i}"].label = f"Horario {i}"

        if self.instance and self.instance.horarios:
            horarios = self.instance.horarios  # lista ejemplo ["10:00", "11:00"]

            # Prellenar por índice
            for i, hora in enumerate(horarios):
                if i < 6:
                    self.fields[f"horario{i+1}"].initial = hora    

    def clean(self):
        cleaned = super().clean()

        horarios = []
        for i in range(1, 7):
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