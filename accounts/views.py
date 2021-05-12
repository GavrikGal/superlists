import uuid
import sys
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.core.mail import send_mail

from accounts.models import Token


def logout(request):
    """выход из системы"""
    auth_logout(request)
    return redirect('/')


def login(request):
    """регистация в системе"""
    print('login view', file=sys.stderr)
    uid = request.GET.get('uid')
    print(f'login. uid = {uid}', file=sys.stderr)
    user = authenticate(uid=uid)
    print(f'login. user = {user}', file=sys.stderr)

    if user is not None:
        auth_login(request, user)
        print(f'login. User not found. New user = {user}', file=sys.stderr)

    return redirect('/')


def send_login_email(request):
    """выслать ссылку на логин по почте"""
    email = request.POST['email']
    uid = str(uuid.uuid4())
    Token.objects.create(email=email, uid=uid)
    print('saving uid', uid, 'for email', email, file=sys.stderr)
    url = request.build_absolute_uri(f'/accounts/login?uid={uid}')
    send_mail(
        'Your login link for Superlists',
        f'Use this link to log in:\n\n{url}',
        'noreply@superlists',
        [email],
    )
    return render(request, 'accounts/login_email_sent.html')
