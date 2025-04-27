from django.db import models
from django.conf import settings

class InteractiveSheet(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('corrected', 'Corrected'),
        ('expired', 'Expired'),
    ]

    subject = models.CharField(max_length=255)  # Asignatura
    statement = models.TextField()  # Enunciado
    is_public = models.BooleanField(default=False)  # Publica
    base_image = models.ImageField(upload_to='interactive_sheets/images/')  # Imagen base
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_sheets'
    )  # Creador (profesor)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )  # Estado
    expiration_date = models.DateTimeField()  # Fecha de expiración
    interactive_options = models.TextField(null=True, blank=True)
    grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )  # Calificación
    comment = models.TextField(null=True, blank=True)  # Comentario
    assigned_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='assigned_sheets', 
        blank=True
    )  # Alumnos asignados
    def __str__(self):
        return f"{self.subject} - {self.creator.username}"
