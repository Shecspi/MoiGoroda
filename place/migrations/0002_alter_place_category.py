# Generated by Django 4.2.17 on 2025-02-11 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='place.category', verbose_name='Категория'),
        ),
    ]
