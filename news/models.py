from django.db import models


class News(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False
    )
    content = models.TextField(
        verbose_name='Описание',
        blank=False
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name='Изменено'
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title
