from django.http import HttpResponse
from .models import RegisterUser
from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
import map.models as ControlModels
from django.contrib import messages
from django.contrib.auth.hashers import check_password

def index(request):
    return render(request, "map/index.html")


def logout_view(request):
    request.session.flush()  # Remove todos os dados da sessão
    return redirect("map:login")  # Redireciona para a página de login


class LoginView(View):
    def get(self, request, *args, **kwargs):
        # Verifica se o usuário já está logado
        if request.session.get('username'):
            return redirect("map:index")
        return render(request, "map/login.html")
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Busca o usuário pelo email
            user = RegisterUser.objects.get(email=email)
            
            # Verifica a senha com check_password
            if check_password(password, user.password):
                request.session['username'] = user.name
                return render(request, "map/index.html")
            else:
                messages.error(request, 'e-mail ou senha errado!')
                return redirect('/map/login/')
        
        except RegisterUser.DoesNotExist:
                messages.error(request, 'e-mail ou senha errado!')
                return redirect('/map/login/')


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        # Verifica se o usuário já está logado
        if request.session.get('username'):
            return redirect("map:index")
    
        return render(request, "map/register.html")
    
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        # Pega os valores para registro
        user = request.POST.get("user")
        user_second = request.POST.get("user_second")
        user_name = user + " " + user_second
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Verifica se o e-mail já existe
        if ControlModels.RegisterUser.objects.filter(email=email).exists():
            messages.error(request, 'O e-mail já está cadastrado. Por favor, use outro e-mail.')
            return redirect('/map/register/')
        # Registra o usuário no banco de dados
        create_user = ControlModels.RegisterUser.objects.create(name=user_name, email=email, password=password)
        create_user.save()
        return redirect("map:login")