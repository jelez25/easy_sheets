from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from .models import Thread, Message
from django.urls import reverse
from django.db.models import Q

@login_required
def thread_list(request):
    threads = Thread.objects.filter(participants=request.user).exclude(id=None).order_by('-updated')
    default_image_url = '/static/accounts/images/blank-profile-picture.png'

    thread_data = []
    for thread in threads:
        other_participant = thread.participants.exclude(id=request.user.id).first()
        other_participant_avatar = other_participant.avatar.url if other_participant and other_participant.avatar else default_image_url
        has_unread = thread.has_unread_messages(request.user)
        thread_data.append({
            'thread': thread,
            'other_participant': other_participant,
            'other_participant_avatar': other_participant_avatar,
            'has_unread': has_unread,
        })

    context = {
        'threads': thread_data,
    }
    return render(request, 'messaging/thread_list.html', context)

@login_required
def start_thread(request, user_id):
    if request.user.id == user_id:
        return redirect('messaging:thread_list')
    other_user = get_object_or_404(CustomUser, id=user_id)    # Solo permitir si ambos están en la misma clase o si uno es profesor y el otro alumno de la misma clase
    same_class = (
        request.user.classroom and other_user.classroom and request.user.classroom_id == other_user.classroom_id
    )
    teacher_student = False
    if request.user.role == 'teacher' and other_user.role == 'student':
        teacher_student = other_user.classroom and other_user.classroom.teacher_id == request.user.id
    elif request.user.role == 'student' and other_user.role == 'teacher':
        teacher_student = request.user.classroom and request.user.classroom.teacher_id == other_user.id
    if not (same_class or teacher_student):
        return redirect('messaging:thread_list')
    # Buscar si ya existe un hilo entre ambos
    thread = Thread.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not thread:
        thread = Thread.objects.create()
        thread.participants.add(request.user, other_user)
    return redirect('messaging:thread_detail', thread_id=thread.id)

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    messages = thread.messages.order_by('timestamp')

    # Marcar mensajes como leídos
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Para iniciar un mensaje nuevo
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(thread=thread, sender=request.user, content=content)
            return redirect('messaging:thread_detail', thread_id=thread.id)    # Para mostrar posibles usuarios con los que iniciar conversación    # Obtener posibles usuarios para chatear basado en el rol
    if request.user.role == 'student':
        # Para estudiantes: mostrar compañeros de clase y profesor
        available_users = CustomUser.objects.filter(
            Q(classroom=request.user.classroom, is_active=True) |  # compañeros
            Q(id=request.user.classroom.teacher.id)  # profesor
        ).exclude(id=request.user.id)
    else:  # teacher
        # Para profesores: mostrar estudiantes de sus clases
        available_users = CustomUser.objects.filter(
            classroom__teacher=request.user,
            role='student',
            is_active=True
        )
    
    other_participant = thread.participants.exclude(id=request.user.id).first()
    default_image_url = '/static/accounts/images/blank-profile-picture.png'

    # Si el otro participante no tiene avatar, usar la imagen por defecto
    other_participant_avatar = other_participant.avatar.url if other_participant and other_participant.avatar else default_image_url

    context = {
        'thread': thread,
        'messages': messages,
        'available_users': available_users,
        'other_participant': other_participant,
        'default_image_url': default_image_url,
        'other_participant_avatar': other_participant_avatar,
    }
    print(f"[View] Rendering thread_detail with thread_id={thread_id}")
    return render(request, 'messaging/thread_detail.html', context)
