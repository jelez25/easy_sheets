from .forms import CustomUserCreationForm, ProfileUpdateForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import CustomUser



# Create your views here.
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'

    def get_success_url(self):
        return reverse_lazy('login') + '?register'

    def form_valid(self, form):
        # Save the user and perform additional actions if needed
        print("Form is valid")
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Pass the logged-in user to the template
        return context

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('profile')
    template_name = 'profile_form.html'

    def get_object(self):
        return self.request.user

    def form_invalid(self, form):
        print("El formulario no es válido")  # Depuración
        print(form.errors)  # Muestra los errores del formulario
        return super().form_invalid(form)

    def form_valid(self, form):
        # Depuración: Verifica si el archivo está en la solicitud
        avatar = self.request.FILES.get('avatar')
        print(f"Archivo recibido: {avatar}")  # Depuración
        instance = form.save(commit=False)
        print(f"Avatar antes de guardar: {instance.avatar}")  # Depuración
        instance.save()
        print(f"Avatar después de guardar: {instance.avatar}")  # Depuración
        return super().form_valid(form)
