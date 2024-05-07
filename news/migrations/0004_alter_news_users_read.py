# Generated by Django 4.2.3 on 2023-12-31 11:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0003_news_users_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='users_read',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
