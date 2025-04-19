from .forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login


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
