# Generated by Django 4.2.17 on 2025-02-18 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('city', '0009_alter_visitedcity_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visitedcity',
            old_name='is_first_time',
            new_name='is_first_visit',
        ),
    ]
