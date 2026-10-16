from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, CustomLoginForm


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')
    
    # Add this method to clear old messages when login page loads
    def get(self, request, *args, **kwargs):
        # Clear messages when user visits login page
        storage = messages.get_messages(request)
        storage.used = True
        return super().get(request, *args, **kwargs)


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')