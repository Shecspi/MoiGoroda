# Generated by Django 4.2.3 on 2023-12-29 11:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0002_alter_news_created_alter_news_last_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='users_read',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]