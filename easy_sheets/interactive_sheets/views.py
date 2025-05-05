from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from .forms import InteractiveSheetForm
from .models import InteractiveSheet
from django.views.generic import ListView, DetailView
import json
# Create your views here.

class CreateSheetView(LoginRequiredMixin, CreateView):
    model = InteractiveSheet
    form_class = InteractiveSheetForm  # Use the custom form
    template_name = 'interactive_sheets/create_sheet.html'
    success_url = '/profile'

    def form_valid(self, form):
        # Ensure the logged-in user is a teacher
        if self.request.user.role != 'teacher':
            return HttpResponseForbidden("You do not have permission to create a sheet.")
        form.instance.creator = self.request.user  # Set the creator as the logged-in user
        return super().form_valid(form)

class TeacherSheetsView(LoginRequiredMixin, ListView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/teacher_sheets_list.html'
    context_object_name = 'sheets'

    def get_queryset(self):
        return InteractiveSheet.objects.filter(creator=self.request.user)

class SheetDetailView(LoginRequiredMixin, DetailView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/sheet_detail.html'
    context_object_name = 'sheet'

class SheetEditView(LoginRequiredMixin, UpdateView):
    model = InteractiveSheet
    fields = ['subject', 'statement', 'base_image', 'is_public', 'expiration_date', 'status']
    template_name = 'interactive_sheets/sheet_edit.html'
    success_url = '/sheets/my-sheets/'

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

class StudentSheetsView(LoginRequiredMixin, ListView):
    model = InteractiveSheet
    template_name = 'interactive_sheets/student_sheets.html'
    context_object_name = 'sheets'

    def get_queryset(self):
        return InteractiveSheet.objects.filter(classrooms__students=self.request.user)