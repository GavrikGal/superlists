from django.contrib.auth.views import auth_logout
from django.urls import path
from accounts import views

urlpatterns = [
    path('send_login_email', views.send_login_email, name='send_login_email'),
    path('login', views.login, name='login'),
    path('logout', auth_logout, {'next_page': '/'}, name='logout'),
]
