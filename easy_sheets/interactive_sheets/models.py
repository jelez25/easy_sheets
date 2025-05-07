from django.db import models
from django.conf import settings
from accounts.models import CustomUser  

class InteractiveSheet(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('corrected', 'Corrected'),
        ('expired', 'Expired'),
        ('assigned', 'Assigned'),
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


class SheetSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    sheet = models.ForeignKey(InteractiveSheet, on_delete=models.CASCADE, related_name='submissions')
    answers = models.JSONField(default=dict)
    submission_date = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('enviada', 'Enviada'), ('corregida', 'Corregida')],
        default='pendiente'
    )

    class Meta:
        unique_together = ['student', 'sheet']  # Un estudiante solo puede enviar una respuesta por ficha

    def __str__(self):
        return f'Submission by {self.student.username} for {self.sheet.subject}'