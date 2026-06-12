from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm
from .models import Invitation

def sign_out(request):
    logout(request)
    messages.success(request, f'You have been logged out.')
    return redirect('account_login')

def invitation(request, code):
    try:
        invite = Invitation.objects.filter(code=code)[0]
    except:
        raise Http404
    if invite.user is not None:
        raise Http404

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            invite.user_id = user.id
            invite.save()
            messages.success(request, 'You have registered successfully.')
            login(request, user)
            return redirect('recipes:my_recipes')
        else:
            return render(request, 'users/invitation.html', {'form': form})
    # else a GET request
    form = RegisterForm()
    return render(request, 'users/invitation.html', {'form': form})
