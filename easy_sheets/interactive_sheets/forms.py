from django import forms
from .models import InteractiveSheet

class InteractiveSheetForm(forms.ModelForm):
    class Meta:
        model = InteractiveSheet
        fields = ['subject', 'statement', 'base_image', 'is_public', 'expiration_date', 'interactive_options']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asignatura'}),
            'statement': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enunciado'}),
            'base_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interactive_options': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Interactive Options (JSON format)'}),
        }
        labels = {
            'subject': 'Asignatura',
            'statement': 'Enunciado',
            'base_image': 'Imagen Base',
            'is_public': '¿Es Pública?',
            'expiration_date': 'Fecha de Expiración',
            'interactive_options': 'Opciones Interactivas',
        }