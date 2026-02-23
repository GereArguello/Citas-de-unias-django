from django.contrib.auth.models import User
from django import forms
from .models import Profile
import re

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