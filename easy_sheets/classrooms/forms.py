from django import forms
from .models import Classroom
from accounts.models import CustomUser

class ClassroomForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),  # Se actualizará dinámicamente
        widget=forms.CheckboxSelectMultiple,  # Cambiado a CheckboxSelectMultiple
        label="Estudiantes",
        required=False
    )

    class Meta:
        model = Classroom
        fields = ['name', 'students']
        widgets = {
            'sheets': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'name': 'Nombre de la Clase',
            'students': 'Alumnos'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == 'teacher':
            # Filtrar estudiantes del mismo colegio que el profesor
            self.fields['students'].queryset = CustomUser.objects.filter(
                role='student',
                school=user.school
            )