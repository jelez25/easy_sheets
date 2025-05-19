from django.db import models
from django.conf import settings
from django.utils.timezone import localtime
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Thread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hilo {self.id} - Participantes: {', '.join([str(u) for u in self.participants.all()])}"

    def has_unread_messages(self, user):
        """
        Verifica si el hilo tiene mensajes no leídos para un usuario específico.
        """
        return self.messages.filter(is_read=False).exclude(sender=user).exists()

class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def formatted_timestamp(self):
        return localtime(self.timestamp).strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"Mensaje de {self.sender} en hilo {self.thread.id}"

# Actualiza el campo `updated` del hilo cuando se crea un nuevo mensaje
@receiver(post_save, sender=Message)
def update_thread_timestamp(sender, instance, **kwargs):
    instance.thread.updated = instance.timestamp
    instance.thread.save()
