from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Classroom
from accounts.models import CustomUser
from .forms import ClassroomForm

# Create your views here.

class ClassroomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'create_classroom.html'
    success_url = '/classrooms/'  # Cambia esta URL según tu proyecto

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario actual al formulario
        return kwargs

    def form_valid(self, form):
        # Asignar el profesor actual como el creador de la clase
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Verificar si el usuario pertenece al grupo "teacher"
        return self.request.user.role == 'teacher'

    def handle_no_permission(self):
        # Redirigir a una página de error o mostrar un mensaje si no tiene permiso
        return redirect('no_permission')  # Cambia 'no_permission' según tu configuración

class ClassroomListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Classroom
    template_name = 'classroom_list.html'
    context_object_name = 'classrooms'

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def test_func(self):
        return self.request.user.role=='teacher'

class ClassroomDetailView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classroom_detail.html'
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.get_object()
        # Filtrar estudiantes disponibles: del mismo colegio y que no están en la clase
        available_students = CustomUser.objects.filter(
            role='student',
            school=self.request.user.school
        ).exclude(enrolled_classrooms=classroom)  # Usar el related_name correcto
        context['available_students'] = available_students
        return context

@login_required
def add_student(request, pk):
    # Verificar si el usuario es un profesor
    if not request.user.role == 'teacher':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    classroom = get_object_or_404(Classroom, pk=pk)

    # Filtrar estudiantes del mismo colegio que el profesor
    students = CustomUser.objects.filter(role='student', school=request.user.school).exclude(enrolled_classrooms=classroom)

    if request.method == 'POST':
        selected_students_ids = request.POST.getlist('students')  # Obtener los IDs seleccionados
        selected_students = CustomUser.objects.filter(id__in=selected_students_ids, role='student', school=request.user.school)
        classroom.students.add(*selected_students)
        return redirect('classroom_detail', pk=classroom.pk)  # Redirigir después de procesar el formulario

    return render(request, 'add_students.html', {'students': students, 'classroom': classroom})

@login_required
def remove_student(request, pk, student_id):
    # Verificar si el usuario es un profesor
    if not request.user.role=='teacher':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    classroom = get_object_or_404(Classroom, pk=pk)
    student = get_object_or_404(CustomUser, pk=student_id)
    classroom.students.remove(student)
    return redirect('classroom_detail', pk=pk)

@login_required
def delete_classroom(request, pk):
    # Verificar si el usuario es un profesor
    if not request.user.role=='teacher':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    classroom = get_object_or_404(Classroom, pk=pk)
    classroom.delete()
    return redirect('classroom_list')
