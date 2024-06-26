# Generated by Django 4.2.3 on 2023-07-28 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('city', '0003_alter_city_date_of_foundation_alter_city_population_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitedcity',
            name='has_magnet',
            field=models.BooleanField(
                blank=True,
                help_text='Отметьте этот пункт, если у Вас есть магнитик с названием города. В списке городов можно будет отфильтровать только те города, которые без магнитов.',
                null=True,
                verbose_name='Наличие магнита',
            ),
        ),
        migrations.AlterField(
            model_name='visitedcity',
            name='impression',
            field=models.TextField(blank=True, null=True, verbose_name='Впечатления о городе'),
        ),
        migrations.AlterField(
            model_name='visitedcity',
            name='rating',
            field=models.SmallIntegerField(
                help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.', verbose_name='Рейтинг'
            ),
        ),
    ]
