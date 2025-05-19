from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import localtime


def custom_upload_to(instance, filename):
    old_instance = CustomUser.objects.get(pk=instance.pk)
    if old_instance.avatar:
        print(f"Eliminando avatar anterior: {old_instance.avatar}")  # Depuración
        old_instance.avatar.delete(save=False)
    ruta = f'accounts/{filename}'
    print(f"Ruta generada para el nuevo avatar: {ruta}")  # Depuración
    return ruta

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)  # Profile picture
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)  # Birth date
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Role field
    name = models.CharField(max_length=150)  # First name
    surname_1 = models.CharField(max_length=150)  # First surname
    surname_2 = models.CharField(max_length=150, blank=True)  # Second surname
    school = models.CharField(max_length=255, default='test_school')
    classroom = models.ForeignKey('classrooms.Classroom', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # Student's classroom

    def formatted_timestamp(self, timestamp):
        """
        Returns the timestamp formatted in the Spanish timezone.
        """
        local_timestamp = localtime(timestamp)
        return local_timestamp.strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"{self.username} ({self.role})"