from django.db import models
from django.conf import settings
from interactive_sheets.models import InteractiveSheet

class Notebook(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del Cuaderno")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notebooks",
        verbose_name="Creador"
    )
    sheets = models.ManyToManyField(
        InteractiveSheet,
        related_name="notebooks",
        blank=True,
        verbose_name="Fichas"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def __str__(self):
        return f"{self.name} ({self.creator.username})"