from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'django_social_app/home.html')

def logout(request):
    auth_logout(request)
    return redirect('/')
