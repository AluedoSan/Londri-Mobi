from django.http import HttpResponse
from .models import RegisterUser
from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import map.models as ControlModels
from django.contrib import messages
from django.contrib.auth.hashers import check_password
import folium

def index(request):
    # Verifica se o usuário está autenticado
    if not request.session.get('username'):
        return redirect('map:login')

    # Cria um mapa centralizado em Londrina, PR
    m = folium.Map(location=[-23.3117, -51.1597], zoom_start=14)

    # Lista de pontos de interesse com suas coordenadas e descrições
    pontos = [
        {
            "location": [-23.3094, -51.1595],
            "tooltip": "Ponto de Aluguel de Bicicletas",
            "popup": "<h1>Bicicleta</h1><p>Rua Sergipe 📍</p>"
        },
        {
            "location": [-23.3183, -51.1627],
            "tooltip": "Ponto de Aluguel no Lago 2",
            "popup": "<h1>Bicicleta</h1><p>Lago 2 📍</p>"
        },
        {
            "location": [-23.3542, -51.1958],
            "tooltip": "Ponto de Aluguel perto do Catuaí",
            "popup": "<h1>Bicicleta</h1><p>Perto do Catuaí Shopping 📍</p>"
        },
        {
            "location": [-23.3431, -51.1626],
            "tooltip": "Ponto de Aluguel no Jardim Botânico",
            "popup": "<h1>Bicicleta</h1><p>Jardim Botânico 📍</p>"
        },
        {
            "location": [-23.3050, -51.1700],
            "tooltip": "Ponto de Aluguel - Calçadão",
            "popup": "<h1>Bicicleta</h1><p>Calçadão de Londrina 📍</p>"
        }
    ]

    # Adiciona os marcadores ao mapa
    for ponto in pontos:
        folium.Marker(
            location=ponto["location"],
            tooltip=ponto["tooltip"],
            popup=ponto["popup"]
        ).add_to(m)

    # Renderiza o mapa como HTML
    map_html = m._repr_html_()  # Gera o HTML do mapa

    # Passa o HTML do mapa para o template
    context = {'map_html': map_html}
    return render(request, "map/index.html", context)

def logout_view(request):
    request.session.flush()  # Remove todos os dados da sessão
    return redirect("map:login")  # Redireciona para a página de login


class LoginView(View):
    def get(self, request, *args, **kwargs):
        # Verifica se o usuário já está logado
        if request.session.get('username'):
            return redirect("map:index")
        return render(request, "map/login.html")
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Busca o usuário pelo email
            user = RegisterUser.objects.get(email=email)
            
            # Verifica a senha com check_password
            if check_password(password, user.password):
                request.session['username'] = user.name
                # Alterado para redirecionar em vez de renderizar
                return redirect("map:index")
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


class RentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "map/rent.html")
    
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        selected_location = request.POST.get("loc")
        context = {"context": selected_location}
        return render(request, "map/rent.html", context)

    
