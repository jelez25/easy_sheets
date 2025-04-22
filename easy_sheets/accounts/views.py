from .forms import CustomUserCreationForm, ProfileUpdateForm, EmailForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import CustomUser
from django import forms
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages

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
        instance = form.save(commit=False)
        instance.save()
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('profile')
    template_name = 'profile_email_form.html'

    def get_object(self):
        # recuperar el objeto que se va editar
        return self.request.user

    def get_form(self, form_class=None):
        form = super(EmailUpdate, self).get_form()
        # Modificar en tiempo real
        form.fields['email'].widget = forms.EmailInput(
            attrs={'class':'form-control mb-2', 'placeholder':'Email'})
        return form

@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('profile')  # Redirect to the profile page after a successful password change

    def form_valid(self, form):
        messages.success(self.request, "Tú Contraseña ha sido cambiada con éxito.")
        return super().form_valid(form)