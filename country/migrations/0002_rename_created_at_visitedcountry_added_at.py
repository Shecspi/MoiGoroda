# Generated by Django 4.2.14 on 2024-09-08 15:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('country', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visitedcountry',
            old_name='created_at',
            new_name='added_at',
        ),
    ]