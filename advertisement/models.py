from colorfield.fields import ColorField
from django.db import models


class LinkAdvertisement(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Отображаемый текст',
        help_text='Текст, который будет виден пользователю как подпись к ссылке',
        blank=False,
    )
    url = models.URLField(
        verbose_name='URL ссылки',
        help_text='Полный адрес перехода, например: https://example.com',
        blank=False,
        null=False,
    )
    legal_marking = models.CharField(
        max_length=255,
        verbose_name='Маркировка рекламы',
        help_text='Текст, который будет отображаться как юридическая маркировка рекламы, например: "Реклама. ООО «Компания». ИНН 1234567890"',
        blank=False,
    )
    color = ColorField(
        default='#FF0000',
        help_text='Цвет текста ссылки в формате HEX, например: #FF0000',
        verbose_name='Цвет ссылки',
        blank=False,
        null=False,
    )
    icon_class = models.CharField(
        max_length=50,
        verbose_name='Класс FontAwesome',
        help_text='CSS-класс иконки FontAwesome, например: fa-solid fa-star',
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рекламная ссылка'
        verbose_name_plural = 'Рекламные ссылки'
