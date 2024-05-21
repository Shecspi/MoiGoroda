# Generated by Django 4.2.13 on 2024-05-21 10:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('city', '0005_alter_visitedcity_has_magnet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitedcity',
            name='has_magnet',
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text='Отметьте этот пункт, если у Вас в коллекции есть сувенир из города. В списке городов можно будет отфильтровать только те города, сувенира из которых у Вас ещё нет.',
                verbose_name='Наличие сувенира из города',
            ),
        ),
    ]
