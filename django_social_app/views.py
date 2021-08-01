from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render


def login(request):
    if request.user.is_authenticated:
        return redirect('etherscan_app:index')
    return render(request, 'django_social_app/login.html')

def logout(request):
    auth_logout(request)
    return redirect('/login')
