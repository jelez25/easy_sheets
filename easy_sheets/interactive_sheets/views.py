from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from .forms import InteractiveSheetForm
from .models import InteractiveSheet, SheetSubmission
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.views import View
from django.urls import reverse
import traceback
# Create your views here.

class CreateSheetView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = InteractiveSheet
    form_class = InteractiveSheetForm  # Use the custom form
    template_name = 'interactive_sheets/create_sheet.html'
    success_url = '/profile'

    def form_valid(self, form):
        form.instance.creator = self.request.user  # Set the creator as the logged-in user
        return super().form_valid(form)

    def test_func(self):
        # Permitir acceso solo a profesores
        return self.request.user.role == 'teacher'

    def handle_no_permission(self):
        # Redirigir a una página de error o mostrar un mensaje
        return redirect('no_permission')  # Cambia 'no_permission' por la URL de tu página de error

class TeacherSheetsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/teacher_sheets_list.html'
    context_object_name = 'sheets'

    def get_queryset(self):
        return InteractiveSheet.objects.filter(creator=self.request.user)

    def test_func(self):
        # Permitir acceso solo a profesores
        return self.request.user.role == 'teacher'
    
    def handle_no_permission(self):
        # Redirigir a una página de error o mostrar un mensaje
        return redirect('no_permission')  # Cambia 'no_permission' por la URL de tu página de error

class SheetEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InteractiveSheet
    fields = ['subject', 'statement', 'base_image', 'is_public', 'expiration_date', 'status']
    template_name = 'interactive_sheets/sheet_edit.html'
    success_url = '/sheets/teacher-sheets/'

    def test_func(self):
        # Permitir acceso solo a profesores
        return self.request.user.role == 'teacher'

class SheetDetailView(LoginRequiredMixin, DetailView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/sheet_detail.html'
    context_object_name = 'sheet'


def interactive_options_api(request, sheet_id):
    """
    Endpoint para obtener los datos interactivos de una ficha.
    """
    sheet = get_object_or_404(InteractiveSheet, id=sheet_id)
    
    # Convertir el campo interactive_options de cadena a JSON
    try:
        interactive_options = json.loads(sheet.interactive_options) if sheet.interactive_options else []
    except json.JSONDecodeError:
        return JsonResponse({'error': 'El campo interactive_options contiene datos no válidos.'}, status=400)

    return JsonResponse(interactive_options, safe=False)

class StudentSheetsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/student_sheets.html'
    context_object_name = 'sheets'

    def get_queryset(self):
        return InteractiveSheet.objects.filter(classrooms__students=self.request.user)

    def test_func(self):
        # Permitir acceso solo a estudiantes
        return self.request.user.role == 'student'

class NoPermissionView(TemplateView):
    template_name = 'interactive_sheets/no_permission.html'

@login_required
def submit_sheet(request, sheet_id):
    if request.method == 'POST':
        try:
            sheet = get_object_or_404(InteractiveSheet, id=sheet_id)
            student = request.user
            if student.role != 'student':
                return JsonResponse({'success': False, 'message': 'No tienes permiso para enviar esta ficha.'}, status=403)

            # Obtener las respuestas del estudiante directamente como JSON
            student_answers = request.POST.get('student_answers', '{}')
            
            # Ya no es necesario hacer json.dumps() aquí, pues ya es una cadena JSON
            
            # Crear o actualizar la entrega
            submission, created = SheetSubmission.objects.update_or_create(
                student=student,
                sheet=sheet,
                defaults={
                    'answers': student_answers,  # Guardar directamente la cadena JSON
                    'status': 'enviada'
                }
            )
            
            # Devolver respuesta JSON exitosa
            return JsonResponse({
                'success': True, 
                'message': 'Ficha enviada correctamente.',
                'redirect_url': reverse('student_sheets')
            })
            
        except Exception as e:
            print(f"Error en submit_sheet: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': f'Error al enviar la ficha: {str(e)}'
            }, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

class SheetSubmissionsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'interactive_sheets/sheet_submissions.html'

    def get(self, request, sheet_id):
        sheet = get_object_or_404(InteractiveSheet, id=sheet_id)
        classroom = sheet.classrooms.first()  # Obtener la primera clase a la que está asignada la ficha
        if not classroom:
            return HttpResponseForbidden("Esta ficha no está asignada a ninguna clase.")

        students_data = []
        for student in classroom.students.all():
            try:
                submission = SheetSubmission.objects.get(sheet=sheet, student=student)
                status = submission.get_status_display()  # Obtener el valor legible del estado
            except SheetSubmission.DoesNotExist:
                status = 'Pendiente'  # Si no hay entrega, el estado es pendiente

            students_data.append({
                'student': student,
                'status': status,
            })

        context = {
            'sheet': sheet,
            'students_data': students_data,
        }
        return render(request, self.template_name, context)

    def test_func(self):
        return self.request.user.role == 'teacher'

@login_required
def view_submission(request, sheet_id):
    sheet = get_object_or_404(InteractiveSheet, id=sheet_id)
    
    # Verificar permisos
    if request.user.role != 'student' and request.user.role != 'teacher':
        return HttpResponseForbidden("No tienes permiso para ver esta entrega.")
    
    # Obtener la entrega para este estudiante
    try:
        if request.user.role == 'student':
            # Estudiantes solo pueden ver sus propias entregas
            submission = SheetSubmission.objects.get(sheet=sheet, student=request.user)
            is_grading = False  # Los estudiantes nunca pueden calificar
            student = request.user
        else:
            # Profesores pueden ver entregas específicas de estudiantes
            student_id = request.GET.get('student_id')
            if student_id:
                submission = SheetSubmission.objects.get(sheet=sheet, student_id=student_id)
                student = get_object_or_404(CustomUser, id=student_id)
                # Comprobar si estamos en modo calificación
                is_grading = request.GET.get('grade') == 'true'
            else:
                # Por defecto, ver todas las entregas
                return redirect('teacher_sheets')
    except SheetSubmission.DoesNotExist:
        messages.error(request, "No se encontró la entrega.")
        return redirect('student_sheets' if request.user.role == 'student' else 'teacher_sheets')
    
    # Procesar formulario de calificación si es POST y estamos en modo calificación
    if request.method == 'POST' and is_grading and request.user.role == 'teacher':
        # Obtener datos del formulario
        feedback = request.POST.get('feedback', '')
        score = request.POST.get('score', None)
        
        # Actualizar la entrega
        submission.feedback = feedback
        
        # Validar y convertir calificación
        try:
            if score:
                score_value = float(score)
                # Asegurarse de que la calificación esté en el rango correcto
                if 0 <= score_value <= 10:
                    submission.score = score_value
                else:
                    messages.error(request, "La calificación debe estar entre 0 y 10.")
            else:
                submission.score = None
        except ValueError:
            messages.error(request, "La calificación debe ser un número válido.")
        
        # Cambiar estado a evaluado
        submission.status = 'corregida'
        submission.save()
        
        messages.success(request, "Entrega calificada correctamente.")
        
        # Redirigir a la lista de entregas con parámetro para no mostrar grade=true
        next_url = request.POST.get('next', reverse('sheet_submissions', kwargs={'sheet_id': sheet_id}))
        return redirect(next_url)
    
    # Convertir las respuestas almacenadas a formato JSON para la plantilla
    student_answers = submission.answers
    
    context = {
        'sheet': sheet,
        'submission': submission,
        'student_answers': student_answers,
        'is_view_only': not is_grading,  # Solo lectura si no estamos calificando
        'is_grading': is_grading,  # Indicar si estamos en modo calificación
        'student': student,
        'back_url': request.GET.get('next', reverse('sheet_submissions', kwargs={'sheet_id': sheet_id}) if request.user.role == 'teacher' else reverse('student_sheets'))
    }
    
    return render(request, 'interactive_sheets/view_submission.html', context)

@login_required
def submission_correction_api(request, sheet_id):
    """
    API para obtener datos necesarios para corregir una entrega.
    Devuelve tanto las opciones interactivas como las respuestas del estudiante.
    """
    # Verificar que el usuario sea profesor
    if request.user.role != 'teacher':
        return JsonResponse({'error': 'No tienes permiso para acceder a esta información'}, status=403)
    
    sheet = get_object_or_404(InteractiveSheet, id=sheet_id)
    student_id = request.GET.get('student_id')
    
    if not student_id:
        return JsonResponse({'error': 'Se requiere ID de estudiante'}, status=400)
    
    # Obtener opciones interactivas
    try:
        interactive_options = json.loads(sheet.interactive_options) if sheet.interactive_options else []
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en formato de opciones interactivas'}, status=500)
    
    # Obtener entrega del estudiante
    try:
        submission = SheetSubmission.objects.get(sheet=sheet, student_id=student_id)
        student = get_object_or_404(CustomUser, id=student_id)
        
        # Obtener las respuestas
        student_answers = {}
        if submission.answers:
            try:
                if isinstance(submission.answers, str):
                    student_answers = json.loads(submission.answers)
                else:
                    student_answers = submission.answers
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Error en formato de respuestas'}, status=500)
        
        # Construir respuesta completa
        response_data = {
            'interactive_options': interactive_options,
            'student_answers': student_answers,
            'submission': {
                'id': submission.id,
                'status': submission.status,
                'status_display': submission.get_status_display(),
                'submission_date': submission.submission_date.isoformat() if submission.submission_date else None,
                'score': submission.score,
                'feedback': submission.feedback
            },
            'student': {
                'id': student.id,
                'name': student.name,
                'surname': student.surname_1,
                'surname2': student.surname_2,
                'email': student.email
            }
        }
        
        return JsonResponse(response_data)
        
    except SheetSubmission.DoesNotExist:
        return JsonResponse({
            'interactive_options': interactive_options,
            'error': 'No se encontró entrega para este estudiante',
            'student': {
                'id': student_id
            }
        })