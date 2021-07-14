from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

def login(request):
    return render(request, 'django_social_app/login.html')

@login_required(login_url='/')
def home(request):
    return render(request, 'django_social_app/home.html')

def logout(request):
    auth_logout(request)
    return redirect('/')
