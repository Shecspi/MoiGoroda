# Generated by Django 4.2.3 on 2023-07-18 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('city', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Название')),
                ('city', models.ManyToManyField(related_name='collections_list', to='city.city')),
            ],
        ),
    ]
