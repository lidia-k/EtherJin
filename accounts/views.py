from django.shortcuts import render, redirect
from accounts.forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("etherscan_app:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request, "accounts/register.html", {"register_form": form})