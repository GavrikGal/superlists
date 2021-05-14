import sys

from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages, auth
from django.urls import reverse


from accounts.models import Token


def login(request):
    """зарегистрировать вход в систему"""
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')


def send_login_email(request):
    """отправить сообщение для входа в систему"""
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
        'Your login link for Superlists',
        message_body,
        'noreply@superlists',
        [email],
    )

    messages.success(
        request,
        "Проверте свою почту мы отправили вам ссылку, которую можно использовать для входа на сайт."
    )
    return redirect('/')
