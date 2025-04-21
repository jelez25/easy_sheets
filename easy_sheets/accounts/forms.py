from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'surname_1', 'surname_2', 'username', 'role', 'email', 'birth_date', 'password1', 'password2']
        labels = {
            'name': 'Nombre',
            'surname_1': 'Primer Apellido',
            'surname_2': 'Segundo Apellido',
            'username': 'Nombre de Usuario',
            'role': 'Rol',
            'email': 'Correo Electrónico',
            'birth_date': 'Fecha de Nacimiento',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'birth_date']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']

    