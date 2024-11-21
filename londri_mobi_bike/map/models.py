from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from datetime import timedelta


class RegisterUser(models.Model):
    """Modelo para usuários registrados."""
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    current_rent = models.OneToOneField(
        'Rent', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='user_renting', verbose_name="Aluguel ativo"
    )  # Relaciona o aluguel atual do usuário, se houver.

    def save(self, *args, **kwargs):
        # Aplica o hash à senha ao salvar um novo registro.
        if not self.pk:  # Só aplica o hash se for um novo registro
            self.password = make_password(self.password)
        super(RegisterUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class BikeStation(models.Model):
    """Modelo para estações de bicicletas."""
    location = models.CharField(max_length=50)
    total_bikes = models.PositiveIntegerField(default=10)  # Quantidade total de bicicletas disponíveis na estação.

    def has_bikes_available(self):
        """Verifica se há bicicletas disponíveis na estação."""
        return self.total_bikes > 0

    def rent_bike(self):
        """Reduz a quantidade de bicicletas disponíveis."""
        if self.has_bikes_available():
            self.total_bikes -= 1
            self.save()

    def return_bike(self):
        """Adiciona uma bicicleta de volta à estação."""
        self.total_bikes += 1
        self.save()

    def __str__(self):
        return f"{self.location} - {self.total_bikes} bicicletas disponíveis"


class Rent(models.Model):
    """Modelo para aluguéis de bicicletas."""
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)  # Relaciona o aluguel ao usuário.
    station = models.ForeignKey(BikeStation, on_delete=models.CASCADE)  # Estação onde a bicicleta foi retirada.
    start_time = models.DateTimeField(default=now)  # Hora do início do aluguel.
    duration = models.PositiveIntegerField()  # Duração do aluguel em minutos.
    is_active = models.BooleanField(default=True)  # Indica se o aluguel ainda está ativo.

    def end_time(self):
        """Calcula a hora em que o aluguel termina."""
        return self.start_time + timedelta(minutes=self.duration)

    def return_bike(self):
        """Finaliza o aluguel e devolve a bicicleta."""
        if self.is_active:
            self.station.return_bike()  # Devolve a bicicleta à estação.
            self.is_active = False
            self.save()

    def __str__(self):
        return f"Aluguel de {self.user.name} na estação {self.station.location} - Ativo: {self.is_active}"
