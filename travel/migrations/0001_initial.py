# Generated by Django 4.1.2 on 2022-10-07 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('type', models.CharField(choices=[('R', 'республика'), ('K', 'край'), ('O', 'область'), ('G', 'город федерального значения'), ('AOb', 'автономная область'), ('AOk', 'автономный округ')], max_length=100, verbose_name='Тип субъекта')),
                ('area', models.ForeignKey(blank=True, default=2, on_delete=django.db.models.deletion.CASCADE, to='travel.area', verbose_name='Федеральный округ')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('population', models.IntegerField(verbose_name='Численность населения')),
                ('date_of_foundation', models.PositiveSmallIntegerField(verbose_name='Год основания')),
                ('coordinate_width', models.FloatField(default=0.0, verbose_name='Широта')),
                ('coordinate_longitude', models.FloatField(default=0.0, verbose_name='Долгота')),
                ('wiki', models.URLField(blank=True, default='', max_length=256, verbose_name='Ссылка на Wikipedia')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.region', verbose_name='Регион')),
            ],
        ),
        migrations.CreateModel(
            name='VisitedCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_visit', models.DateField(verbose_name='Дата посещения')),
                ('has_magnet', models.BooleanField(default=False, verbose_name='Наличие магнита')),
                ('impression', models.TextField(default='', null=True, verbose_name='Впечатления о городе')),
                ('rating', models.SmallIntegerField(default=0, null=True, verbose_name='Рейтинг')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.city', verbose_name='Город')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel.region', verbose_name='Регион')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'unique_together': {('user', 'region', 'city')},
            },
        ),
    ]
