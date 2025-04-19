from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)  # Profile picture
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)  # Birth date
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Role field

    def __str__(self):
         return f"{self.username} ({self.role})"