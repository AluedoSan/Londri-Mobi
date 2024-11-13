from django.db import models
from django.contrib.auth.hashers import make_password

class RegisterUser(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        # Antes de salvar, hash da senha
        if not self.pk:  # Só aplica o hash se for um novo registro
            self.password = make_password(self.password)
        super(RegisterUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
