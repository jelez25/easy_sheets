import uuid
from django.db import models
from django.conf import settings
from interactive_sheets.models import InteractiveSheet

class Classroom(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Clase")
    class_code = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        verbose_name="Código de Clase"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="Profesor"
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_classrooms",
        blank=True,
        verbose_name="Alumnos"
    )
    sheets = models.ManyToManyField(
        InteractiveSheet,
        related_name="classrooms",
        blank=True,
        verbose_name="Fichas Asignadas"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def save(self, *args, **kwargs):
        # Generar un código único para la clase si no existe
        if not self.class_code:
            self.class_code = str(uuid.uuid4())[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.class_code})"
