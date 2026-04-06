import city.models
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import MoiGoroda.storages


class Migration(migrations.Migration):
    dependencies = [
        ('city', '0030_alter_visitedcity_impression_help_text'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CityUserPhoto',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'image',
                    models.ImageField(
                        storage=MoiGoroda.storages.UsersCityPhotoStorage(),
                        upload_to=city.models.city_user_photo_upload_to,
                        verbose_name='Изображение',
                    ),
                ),
                ('is_default', models.BooleanField(default=False, verbose_name='Фото по умолчанию')),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name='Позиция')),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания'),
                ),
                (
                    'updated_at',
                    models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения'),
                ),
                (
                    'city',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='user_photos',
                        to='city.city',
                        verbose_name='Город',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='city_photos',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Пользовательское фото города',
                'verbose_name_plural': 'Пользовательские фото городов',
                'ordering': ['position', '-created_at'],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('user', 'city', 'position'), name='unique_city_user_photo_position'
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(('is_default', True)),
                        fields=('user', 'city'),
                        name='unique_city_user_default_photo',
                    ),
                ],
            },
        ),
    ]
