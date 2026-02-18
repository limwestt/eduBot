from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import UserProfile
from django.db.models import Sum

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue sur EduBot.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')

@login_required
def dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    total_quiz = profile.user.quizattempt_set.count() if hasattr(profile.user, 'quizattempt_set') else 0
    moyenne = profile.score_total / max(total_quiz, 1)
    
    context = {
        'profile': profile,
        'total_quiz': total_quiz,
        'moyenne': round(moyenne, 1),
    }
    return render(request, 'accounts/dashboard.html', context)
