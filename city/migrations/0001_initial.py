# Generated by Django 4.2.3 on 2023-07-18 04:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('region', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('population', models.PositiveIntegerField(blank=True, default=0, verbose_name='Численность населения')),
                ('date_of_foundation', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Год основания')),
                ('coordinate_width', models.FloatField(verbose_name='Широта')),
                ('coordinate_longitude', models.FloatField(verbose_name='Долгота')),
                ('wiki', models.URLField(blank=True, default='', max_length=256, verbose_name='Ссылка на Wikipedia')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='VisitedCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_visit', models.DateField(blank=True, help_text='Укажите дату посещения города. На основе этой даты будет происходить сортировка городов, а также это влияет на отображаемую статистику посещённых городов за год.', null=True, verbose_name='Дата посещения')),
                ('has_magnet', models.BooleanField(help_text='Отметьте этот пункт, если у Вас есть магнитик с названием города. В списке городов можно будет отфильтровать только те города, которые без магнитов.', verbose_name='Наличие магнита')),
                ('impression', models.TextField(blank=True, default='', verbose_name='Впечатления о городе')),
                ('rating', models.SmallIntegerField(default=0, help_text='fdsf', verbose_name='Рейтинг')),
                ('city', models.ForeignKey(help_text='Выберите город, который посетили.', on_delete=django.db.models.deletion.CASCADE, related_name='visitedcity', to='city.city', verbose_name='Город')),
                ('region', models.ForeignKey(help_text='Выберите регион, в котором находится посещённый город. Список городов выбранного региона подгрузится автоматически в поле "Город".', on_delete=django.db.models.deletion.CASCADE, to='region.region', verbose_name='Регион')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Посещённый город',
                'verbose_name_plural': 'Посещённые города',
            },
        ),
    ]
