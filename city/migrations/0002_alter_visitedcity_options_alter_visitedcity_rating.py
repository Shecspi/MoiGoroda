# Generated by Django 4.2.3 on 2023-07-24 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visitedcity',
            options={'ordering': ['-id'], 'verbose_name': 'Посещённый город', 'verbose_name_plural': 'Посещённые города'},
        ),
        migrations.AlterField(
            model_name='visitedcity',
            name='rating',
            field=models.SmallIntegerField(default=0, help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.', verbose_name='Рейтинг'),
        ),
    ]