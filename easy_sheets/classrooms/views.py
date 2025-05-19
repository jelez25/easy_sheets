from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import UpdateView
from .models import Classroom
from accounts.models import CustomUser
from interactive_sheets.models import InteractiveSheet, SheetSubmission
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
        # Filtrar estudiantes disponibles (sin clase asignada)
        available_students = CustomUser.objects.filter(
            role='student',
            school=self.request.user.school,
            classroom__isnull=True
        )
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

    # Filtrar estudiantes del mismo colegio que el profesor que no estén en ninguna clase
    students = CustomUser.objects.filter(
        role='student', 
        school=request.user.school,
        classroom__isnull=True
    )

    if request.method == 'POST':
        selected_students_ids = request.POST.getlist('students')  # Obtener los IDs seleccionados
        selected_students = CustomUser.objects.filter(
            id__in=selected_students_ids, 
            role='student', 
            school=request.user.school,
            classroom__isnull=True
        )
        # Actualizar el aula de cada estudiante
        for student in selected_students:
            student.classroom = classroom
            student.save()
            
            # Crear SheetSubmission para el estudiante con todas las fichas de la clase
            for sheet in classroom.sheets.all():
                SheetSubmission.objects.get_or_create(student=student, sheet=sheet)
                
        messages.success(request, "Estudiantes añadidos correctamente.")
        return redirect('edit_classroom', pk=classroom.pk)

    return render(request, 'add_students.html', {'students': students, 'classroom': classroom})

@login_required
def remove_student(request, pk, student_id):
    # Verificar si el usuario es un profesor
    if not request.user.role=='teacher':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    classroom = get_object_or_404(Classroom, pk=pk)
    student = get_object_or_404(CustomUser, pk=student_id)
    
    # Solo remover si el estudiante está en esta clase
    if student.classroom == classroom:
        # Eliminar todas las entregas pendientes del estudiante para las fichas de esta clase
        SheetSubmission.objects.filter(student=student, sheet__in=classroom.sheets.all()).delete()
        
        # Remover al estudiante de la clase
        student.classroom = None
        student.save()
    
    return redirect('edit_classroom', pk=pk)

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
    
    # Verificar si el usuario es un profesor
    if not request.user.role == 'teacher':
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        sheet_id = request.POST.get('sheets')
        if sheet_id:
            sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)
            
            # Cambiar el estado de la ficha a "assigned"
            sheet.status = 'assigned'
            sheet.save()  # Guardar el cambio de estado
            
            # Añadir la ficha a la clase
            classroom.sheets.add(sheet)

            # Crear SheetSubmission para cada estudiante de la clase
            for student in classroom.students.all():
                SheetSubmission.objects.create(student=student, sheet=sheet)
            
            return redirect('edit_classroom', pk=classroom.pk)

    return redirect('edit_classroom', pk=classroom.pk)

@login_required
def remove_sheet(request, pk, sheet_id):
    # Obtener la clase y la ficha
    classroom = get_object_or_404(Classroom, pk=pk)
    sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)

    # Verificar si el método es POST
    if request.method == 'POST':
        # Eliminar la ficha de la clase
        classroom.sheets.remove(sheet)

        # Eliminar todos los SheetSubmission asociados a la ficha y a los estudiantes de la clase
        SheetSubmission.objects.filter(sheet=sheet, student__in=classroom.students.all()).delete()

        return redirect('edit_classroom', pk=classroom.pk)

    # Redirigir a la página de detalles de la clase si no es POST
    return redirect('edit_classroom', pk=classroom.pk)

class StudentClassroomView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classrooms/student_classroom.html'
    context_object_name = 'classroom'

    def get_object(self):
        # Obtener la clase a la que el estudiante está asignado
        return self.request.user.classroom

    def get(self, request, *args, **kwargs):
        classroom = self.get_object()
        if classroom:
            return super().get(request, *args, **kwargs)
        else:
            # Si el estudiante no está asignado a ninguna clase, redirigir a una página para unirse
            return redirect('join_classroom')

class JoinClassroomView(LoginRequiredMixin, View):
    def post(self, request):
        class_code = request.POST.get('class_code')
        try:
            # Filtrar la clase por código y colegio del estudiante
            classroom = Classroom.objects.get(class_code=class_code, teacher__school=request.user.school)
            
            # Verificar que el estudiante no esté ya en una clase
            if request.user.classroom is not None:
                return render(request, 'classrooms/join_classroom.html', {
                    'error': 'Ya estás asignado a una clase. Debes salir de tu clase actual antes de unirte a otra.'
                })
                
            # Asignar el estudiante a la clase
            request.user.classroom = classroom
            request.user.save()
            
            # Crear SheetSubmission para todas las fichas de la clase
            for sheet in classroom.sheets.all():
                SheetSubmission.objects.get_or_create(student=request.user, sheet=sheet)
            
            return HttpResponseRedirect(reverse('student_classroom'))
        except Classroom.DoesNotExist:
            # Mostrar un mensaje de error si la clase no existe o no pertenece al mismo colegio
            return render(request, 'classrooms/join_classroom.html', {
                'error': 'El código de clase no es válido o no pertenece a tu colegio.'
            })

    def get(self, request):
        return render(request, 'classrooms/join_classroom.html')

class ClassroomEditView(LoginRequiredMixin, DetailView):
    model = Classroom
    template_name = 'classrooms/edit_classroom.html'
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classroom = self.get_object()
        # Filtrar estudiantes disponibles (sin clase asignada)
        available_students = CustomUser.objects.filter(
            role='student',
            school=self.request.user.school,
            classroom__isnull=True
        )
        # Filtrar fichas disponibles
        available_sheets = InteractiveSheet.objects.exclude(classrooms=classroom)
        context['available_students'] = available_students
        context['available_sheets'] = available_sheets
        return context