from django.http import HttpResponse
from .models import RegisterUser, Rent, BikeStation
from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import map.models as ControlModels
from django.contrib import messages
from django.contrib.auth.hashers import check_password
import folium
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404


def index(request):
    # Verifica se o usuário está autenticado
    if not request.session.get('username'):
        return redirect('map:login')
    
    # Busca o usuário logado
    user_name = request.session.get('username')
    user = get_object_or_404(RegisterUser, name=user_name)

    # Busca todos os aluguéis ativos do usuário
    rents = Rent.objects.filter(user=user, is_active=True)

    # Pega a quantidade de bicicletas por estação
    centro_bikes = ControlModels.BikeStation.objects.filter(location="centro").first()
    lago_bikes = ControlModels.BikeStation.objects.filter(location="lago").first()
    calcadao_bikes = ControlModels.BikeStation.objects.filter(location="calcadao").first()
    jardim_bikes = ControlModels.BikeStation.objects.filter(location="jardim").first()
    catuai_bikes = ControlModels.BikeStation.objects.filter(location="catuai").first()

    # Cria um mapa centralizado em Londrina, PR
    m = folium.Map(location=[-23.3117, -51.1597], zoom_start=14)

    # Lista de pontos de interesse com suas coordenadas e descrições
    pontos = [
        {
            "location": [-23.3094, -51.1595],
            "tooltip": "Ponto de Aluguel de Bicicletas",
            "popup": "<h2>Rua Sergipe 📍</h2>",
            "bikes": f"{centro_bikes.total_bikes}"
        },
        {
            "location": [-23.3183, -51.1627],
            "tooltip": "Ponto de Aluguel no Lago 2",
            "popup": "<h2>Lago 2 📍</h2>",
            "bikes": f"{lago_bikes.total_bikes}"
        },
        {
            "location": [-23.3542, -51.1958],
            "tooltip": "Ponto de Aluguel perto do Catuaí",
            "popup": "<h2>Perto do Catuaí Shopping 📍</h2>",
            "bikes": f"{catuai_bikes.total_bikes}"
        },
        {
            "location": [-23.3431, -51.1626],
            "tooltip": "Ponto de Aluguel no Jardim Botânico",
            "popup": "<h2>Jardim Botânico 📍</h2>",
            "bikes": f"{jardim_bikes.total_bikes}"
        },
        {
            "location": [-23.3050, -51.1700],
            "tooltip": "Ponto de Aluguel - Calçadão",
            "popup": "<h2>Calçadão de Londrina 📍</h2>",
            "bikes": f"{calcadao_bikes.total_bikes}"
        }
    ]

    # Adiciona os marcadores ao mapa
    for ponto in pontos:
        folium.Marker(
            location=ponto["location"],
            tooltip=ponto["tooltip"],
            popup=f"{ponto['popup']}<p>Disponível: {ponto['bikes']} bicicletas</p>"
        ).add_to(m)

    # Renderiza o mapa como HTML
    map_html = m._repr_html_()  # Gera o HTML do mapa

    # Tratamento da duração do aluguel
    def format_duration(minutes):
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if hours > 0:
            return f"{hours} hora{'s' if hours > 1 else ''} e {remaining_minutes} minuto{'s' if remaining_minutes > 1 else ''}"
        else:
            return f"{remaining_minutes} minuto{'s' if remaining_minutes > 1 else ''}"

    # Formata a duração de cada aluguel
    for rent in rents:
        rent.formatted_duration = format_duration(rent.duration)

    # Passa as informações para o template
    context = {
        'map_html': map_html,
        'rents': rents,  # Passa os aluguéis ativos para o contexto
    }

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
        # Verifica se o usuário já está logado
        if not request.session.get('username'):
            return redirect("map:login")

        # Captura o valor do local selecionado no parâmetro 'loc'
        location = request.GET.get("loc", None)
        context = {"selected_location": location}
        return render(request, "map/rent.html", context)

    def post(self, request, *args, **kwargs):
        # Verifica se o usuário está logado
        if not request.session.get('username'):
            return redirect("map:login")

        # Captura os dados do formulário
        location_name = request.POST.get("location")  # Local da estação
        rent_time = int(request.POST.get("tempo"))  # Tempo selecionado em minutos ou horas

        # Busca a estação de bicicletas
        station = get_object_or_404(BikeStation, location=location_name)

        # Busca o usuário logado
        user_name = request.session.get('username')
        user = get_object_or_404(RegisterUser, name=user_name)

        # Verifica disponibilidade de bicicletas
        if not station.has_bikes_available():
            messages.error(request, "Desculpe, não há bicicletas disponíveis nesta estação.")
            return redirect("map:rent")

        # Aluga a bicicleta na estação
        station.rent_bike()

        # Cria um novo registro de aluguel
        Rent.objects.create(
            user=user,
            station=station,
            duration=rent_time,
            start_time=datetime.now(),
        )

        # Atualiza o status do usuário
        user.rented_bike = True
        user.rent_station = station
        user.save()

        # Mensagem de sucesso e redirecionamento
        messages.success(request, f"Você alugou uma bicicleta na estação {station.location} por {rent_time} minutos.")
        return redirect("map:index")


    
@csrf_protect
def redict_rent(request):
    if request.method == "POST":
        selected_location = request.POST.get("loc")
        context = {"context": selected_location}
        return render(request, "map/rent.html", context)
    else:
        return redirect("map:index")  # Redireciona para a página inicial se não for POST
    

class Command(BaseCommand):
    help = "Verifica aluguéis expirados e retorna bicicletas às estações"

    def handle(self, *args, **kwargs):
        expired_rents = Rent.objects.filter(is_active=True, start_time__lt=now())

        for rent in expired_rents:
            # Atualiza a estação, devolvendo uma bicicleta
            station = rent.station
            station.total_bikes += 1
            station.save()

            # Marca o aluguel como inativo
            rent.is_active = False
            rent.save()

            self.stdout.write(self.style.SUCCESS(f"Bicicleta devolvida: {rent}"))


