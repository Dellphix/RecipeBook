from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import LoginForm, RegisterForm
from .models import Invitation


def sign_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # messages.success(request, f'Hi {username.title()}, welcome back!')
                if request.GET and request.GET['redirect_to']:
                    return redirect(request.GET['redirect_to'])
                return redirect('recipes:my_recipes')

        # form is not valid or user is not authenticated
        messages.error(request, f'Invalid username or password')
        return render(request, 'users/login.html', {'form': form})
    # else a GET request
    form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def sign_out(request):
    logout(request)
    messages.success(request, f'You have been logged out.')
    return redirect('login')

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
