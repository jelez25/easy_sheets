from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notebook
from interactive_sheets.models import InteractiveSheet

class CreateNotebookView(LoginRequiredMixin, CreateView):
    model = Notebook
    fields = ['name']
    template_name = 'notebooks/create_notebook.html'
    success_url = reverse_lazy('list_notebooks')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
        return super().dispatch(request, *args, **kwargs)

class ListNotebooksView(LoginRequiredMixin, ListView):
    model = Notebook
    template_name = 'notebooks/list_notebooks.html'
    context_object_name = 'notebooks'

    def get_queryset(self):
        return Notebook.objects.filter(creator=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
        return super().dispatch(request, *args, **kwargs)

class NotebookDetailView(LoginRequiredMixin, DetailView):
    model = Notebook
    template_name = 'notebooks/notebook_detail.html'
    context_object_name = 'notebook'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
        return super().dispatch(request, *args, **kwargs)

class EditNotebookView(LoginRequiredMixin, UpdateView):
    model = Notebook
    fields = []  # Fields are managed manually in the form
    template_name = 'notebooks/edit_notebook.html'
    success_url = None  # Override success_url to dynamically redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_sheets'] = InteractiveSheet.objects.filter(creator=self.request.user).exclude(id__in=self.object.sheets.values_list('id', flat=True))
        context['assigned_sheets'] = self.object.sheets.all()
        return context

    def form_valid(self, form):
        sheet_ids_to_add = self.request.POST.getlist('add_sheets')
        sheet_ids_to_remove = self.request.POST.getlist('remove_sheets')

        # Add selected sheets
        sheets_to_add = InteractiveSheet.objects.filter(id__in=sheet_ids_to_add)
        self.object.sheets.add(*sheets_to_add)

        # Remove selected sheets
        sheets_to_remove = InteractiveSheet.objects.filter(id__in=sheet_ids_to_remove)
        self.object.sheets.remove(*sheets_to_remove)

        messages.success(self.request, "Cuaderno actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('notebook_detail', kwargs={'pk': self.object.pk})

class DeleteNotebookView(LoginRequiredMixin, DeleteView):
    model = Notebook
    template_name = 'notebooks/delete_notebook.html'
    success_url = reverse_lazy('list_notebooks')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cuaderno eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            return HttpResponseForbidden("No tienes permiso para realizar esta acción.")
        return super().dispatch(request, *args, **kwargs)

@login_required
def add_sheet_to_notebook(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk)

    if request.method == 'POST':
        sheet_id = request.POST.get('sheets')
        if sheet_id:
            sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)
            notebook.sheets.add(sheet)
            messages.success(request, "Ficha añadida correctamente al cuaderno.")
        return redirect('edit_notebook', pk=notebook.pk)

    return HttpResponseForbidden("Método no permitido.")

@login_required
def remove_sheet_from_notebook(request, pk, sheet_id):
    notebook = get_object_or_404(Notebook, pk=pk)
    sheet = get_object_or_404(InteractiveSheet, pk=sheet_id)

    if request.method == 'POST':
        notebook.sheets.remove(sheet)
        messages.success(request, "Ficha eliminada correctamente del cuaderno.")
        return redirect('edit_notebook', pk=notebook.pk)

    return HttpResponseForbidden("Método no permitido.")