from django.contrib.auth.models import User
from django.db import models


def custom_directory_path(instance, filename):
    """
    Возвращает строку с адресом для сохранения картинок.
    Файл имеет название такое же, как и поле 'name', расширение оригинальное, а папка - первая буква названия.
    """
    return 'collection/{0}/{1}.{2}'.format(instance.name[:1], instance.name, filename.split('.')[-1:])


class Collection(models.Model):
    """
    Таблица, хранящая названия коллекций и их логотипы.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to=custom_directory_path
    )

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

    def __str__(self):
        return self.name


class Achievement(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        verbose_name='Коллекция'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
