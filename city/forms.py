"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from city.models import VisitedCity, City


class VisitedCity_Create_Form(ModelForm):
    CHOICES = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    rating = forms.ChoiceField(
        label='Оценка города',
        choices=CHOICES,
        widget=forms.RadioSelect,
        help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.',
    )

    class Meta:
        model = VisitedCity
        # date_of_visit указан первым, чтобы во время проверки city параметр date_of_visit был доступен
        fields = ['date_of_visit', 'region', 'city', 'has_magnet', 'impression', 'rating']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('Save', 'Сохранить'))
        self.helper.layout = Layout(
            Row(
                Column('region', css_class='col-xl-4'),
                Column('city', css_class='col-xl-4'),
                HTML("{% include 'city/select_date_input.html' %}"),
                css_class='g-3',
            ),
            Row(
                Column('has_magnet', css_class='col-xl-6'),
                Column(InlineRadios('rating'), css_id='col-xl-6'),
                css_class='mt-3 g-3',
            ),
            Row(Column('impression'), css_class='mt-3'),
        )

        self.fields['impression'].required = False

        # По-умолчанию элемент <select> для выбора городов - пустой, пока не будет выбран регион.
        # Но при загрузке страницы после возникновения ошибки - поле заполняется списком городов.
        if not self.errors:
            self.fields['city'].queryset = City.objects.none()

        # Код ниже необходим для корректной обработки формы после подгрузки списка городов.
        # Так как по-умолчанию список городов is None, поэтому его нужно дозагрузить при проверке формы
        if 'region' in self.data:
            region_id = int(self.data.get('region'))
            self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by(
                'title'
            )
            # Если форма не отправлена (GET) и есть выбранный город через initial
        elif self.initial.get('city'):
            try:
                selected_city = City.objects.get(pk=self.initial['city'])
                self.fields['city'].queryset = City.objects.filter(
                    region=selected_city.region
                ).order_by('title')
                self.initial['region'] = (
                    selected_city.region_id
                )  # также заполняем initial значение для поля "region"
            except City.DoesNotExist:
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.region.city_set.order_by('title')

        print(self.fields['date_of_visit'])

    def clean_city(self) -> City:
        """
        Проверка корректности заполнения поля 'City'.
        Не допускается создание записей с одинаковыми 'user', 'region', 'city' и 'date_of_visit'.
        """
        city = self.cleaned_data['city']
        date_of_visit = self.cleaned_data['date_of_visit']

        # Для того чтобы во время редактирования не проверялось существование аналогичной записи,
        # удаляем её из результатов запроса.
        db_city = VisitedCity.objects.filter(
            user_id=self.request.user,
            region=self.cleaned_data['region'],
            city=city,
            date_of_visit=date_of_visit,
        ).exclude(id=self.instance.id)

        if db_city.exists():
            raise ValidationError(
                f'Город "{city}" уже был отмечен Вами как посещённый {date_of_visit.strftime('%d.%m.%Y') if date_of_visit else "без указания даты"}'
            )

        return city

    def clean_rating(self) -> str:
        """
        Проверка корректности заполнения поля 'Rating'.
        Рейтинг должен быть в диапазоне от 1 до 5.
        """
        rating = int(self.cleaned_data['rating'])

        if rating < 1 or rating > 5:
            raise ValidationError('Оценка должна быть в диапазоне от 1 до 5.')

        return rating
