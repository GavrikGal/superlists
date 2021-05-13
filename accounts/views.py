from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages


def send_login_email(request):
    """отправить сообщение для входа в систему"""
    email = request.POST['email']
    send_mail(
        'Your login link for Superlists',
        'body text tbc',
        'noreply@superlists',
        [email],
    )

    messages.success(
        request,
        "Проверте совю почту мы отправили вам ссылку, которую можно использовать для входа на сайт."
    )
    return redirect('/')
