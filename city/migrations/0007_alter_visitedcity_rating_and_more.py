# Generated by Django 4.2.14 on 2024-08-02 11:47

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("city", "0006_alter_visitedcity_has_magnet"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visitedcity",
            name="rating",
            field=models.SmallIntegerField(
                help_text="Поставьте оценку городу. 1 - плохо, 5 - отлично.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
                verbose_name="Рейтинг",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="visitedcity",
            unique_together={("user", "city")},
        ),
    ]
