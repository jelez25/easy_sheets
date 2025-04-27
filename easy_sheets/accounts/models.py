from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)  # Profile picture
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)  # Birth date
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Role field
    name = models.CharField(max_length=150)  # First name
    surname_1 = models.CharField(max_length=150)  # First surname
    surname_2 = models.CharField(max_length=150, blank=True)  # Second surname
    school = models.CharField(max_length=255, default='test_school')

    def __str__(self):
        return f"{self.username} ({self.role})"

@receiver(pre_save, sender=CustomUser)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            if old_instance.avatar and old_instance.avatar != instance.avatar:
                old_instance.avatar.delete(save=False)
        except CustomUser.DoesNotExist:
            pass

@receiver(post_delete, sender=CustomUser)
def delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)