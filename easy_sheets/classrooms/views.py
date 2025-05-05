from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Classroom
from accounts.models import CustomUser
from interactive_sheets.models import InteractiveSheet
from .forms import ClassroomForm

# Create your views here.

class ClassroomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'classrooms/create_classroom.html'
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
    template_name = 'classrooms/classroom_list.html'
    context_object_name = 'classrooms'

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def test_func(self):
        return self.request.user.role=='teacher'

class ClassroomDetailView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classrooms/classroom_detail.html'
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.get_object()
        # Filtrar estudiantes disponibles
        available_students = CustomUser.objects.filter(
            role='student',
            school=self.request.user.school
        ).exclude(enrolled_classrooms=classroom)
        # Filtrar fichas disponibles
        available_sheets = InteractiveSheet.objects.exclude(classrooms=classroom)
        context['available_students'] = available_students
        context['available_sheets'] = available_sheets
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

@login_required
def assign_sheet(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        sheet_id = request.POST.get('sheets')
        if sheet_id:
            sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)
            classroom.sheets.add(sheet)
            return redirect('classroom_detail', pk=classroom.pk)

    return redirect('classroom_detail', pk=classroom.pk)

@login_required
def remove_sheet(request, pk, sheet_id):
    # Obtener la clase y la ficha
    classroom = get_object_or_404(Classroom, pk=pk)
    sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)

    # Verificar si el método es POST
    if request.method == 'POST':
        # Eliminar la ficha de la clase
        classroom.sheets.remove(sheet)
        return redirect('classroom_detail', pk=classroom.pk)

    # Redirigir a la página de detalles de la clase si no es POST
    return redirect('classroom_detail', pk=classroom.pk)

class StudentClassroomView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classrooms/student_classroom.html'
    context_object_name = 'classroom'

    def get_object(self):
        # Obtener la clase a la que el estudiante está asignado
        try:
            return Classroom.objects.get(students=self.request.user)
        except Classroom.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        classroom = self.get_object()
        if classroom:
            return super().get(request, *args, **kwargs)
        else:
            # Si el estudiante no está asignado a ninguna clase, redirigir a una página para unirse
            return redirect('join_classroom')  # Cambia 'join_classroom' según tu configuración

class JoinClassroomView(LoginRequiredMixin, View):
    def post(self, request):
        class_code = request.POST.get('class_code')
        try:
            # Filtrar la clase por código y colegio del estudiante
            classroom = Classroom.objects.get(class_code=class_code, teacher__school=request.user.school)
            classroom.students.add(request.user)
            return HttpResponseRedirect(reverse('student_classroom'))
        except Classroom.DoesNotExist:
            # Mostrar un mensaje de error si la clase no existe o no pertenece al mismo colegio
            return render(request, 'classrooms/join_classroom.html', {
                'error': 'El código de clase no es válido o no pertenece a tu colegio.'
            })

    def get(self, request):
        return render(request, 'classrooms/join_classroom.html')