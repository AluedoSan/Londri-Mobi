# Generated by Django 5.1.3 on 2024-11-21 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0005_alter_bikerent_qntd_alter_registeruser_rent_bike'),
    ]

    operations = [
        migrations.AddField(
            model_name='bikerent',
            name='hour',
            field=models.DateField(null=True, verbose_name='Horario alugado'),
        ),
    ]
