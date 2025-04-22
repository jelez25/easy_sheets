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

class EmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Requerido. 254 carácteres como máximo y debe ser válido.")

    class Meta:
        model = CustomUser
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if 'email' in self.changed_data:
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("El email ya está registrado, prueba con otro.")
        return email