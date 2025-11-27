"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from city.models import VisitedCity, City
from country.models import Country
from region.models import Region


class VisitedCity_Create_Form(ModelForm):  # type: ignore[type-arg]
    CHOICES = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    rating = forms.ChoiceField(
        label='Оценка города',
        choices=CHOICES,
        widget=forms.RadioSelect,
        help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.',
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(city__isnull=False).distinct().order_by('name'),
        required=True,
        empty_label='Выберите страну',
        label='Страна',
        help_text='Выберите страну для фильтрации регионов',
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('title'),
        required=False,
        empty_label='Выберите регион',
        label='Регион',
        help_text='Выберите регион для фильтрации городов',
    )

    class Meta:
        model = VisitedCity
        # date_of_visit указан первым, чтобы во время проверки city параметр date_of_visit был доступен
        fields = [
            'date_of_visit',
            'city',
            'has_magnet',
            'impression',
            'rating',
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)

        self.fields['impression'].required = False
        # Применяем стили к textarea
        base_classes = 'block w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200 dark:placeholder:text-neutral-500 dark:focus:ring-neutral-600'
        if self.errors and 'impression' in self.errors:
            base_classes += ' border-red-500 dark:border-red-500'
        self.fields['impression'].widget.attrs.update(
            {
                'class': base_classes,
                'rows': '4',
            }
        )

        # По-умолчанию элемент <select> для выбора городов - пустой, пока не будет выбран регион.
        # Но при загрузке страницы после возникновения ошибки - поле заполняется списком городов.
        if not self.errors:
            self.fields['city'].queryset = City.objects.none()  # type: ignore[attr-defined]

        # Код ниже необходим для корректной обработки формы после подгрузки списка городов.
        # Так как по-умолчанию список городов is None, поэтому его нужно дозагрузить при проверке формы
        if 'region' in self.data:
            region_id_str = self.data.get('region')
            if region_id_str:
                region_id = int(region_id_str)
                self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by(  # type: ignore[attr-defined]
                    'title'
                )
            # Если форма не отправлена (GET) и есть выбранный город через initial
        elif self.initial.get('city'):
            try:
                selected_city = City.objects.get(pk=self.initial['city'])
                self.fields['city'].queryset = City.objects.filter(  # type: ignore[attr-defined]
                    region=selected_city.region
                ).order_by('title')
                self.initial['region'] = (
                    selected_city.region_id
                )  # также заполняем initial значение для поля "region"
            except City.DoesNotExist:
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.region.city_set.order_by('title')  # type: ignore[attr-defined]

        # Ограничиваем список регионов только регионами выбранной страны
        # По умолчанию отображаем показываем регионы России
        country_id = self.initial.get('country')
        if country_id:
            try:
                country_id_int = int(country_id)
                self.fields['region'].queryset = Region.objects.filter(  # type: ignore[attr-defined]
                    country_id=country_id_int
                ).order_by('title')

                if not self.fields['region'].queryset.exists():  # type: ignore[attr-defined]
                    self.fields['region'].disabled = True
                else:
                    self.fields['region'].disabled = False
            except (ValueError, TypeError):
                self.fields['region'].queryset = Region.objects.none()  # type: ignore[attr-defined]
        else:
            self.fields['region'].queryset = Region.objects.filter(country_id=171)  # type: ignore[attr-defined]

        # По-умолчанию делаем Россию выбранной страной
        if not self.initial.get('country'):
            try:
                default_country = Country.objects.get(pk=171)
                self.initial['country'] = default_country.pk
            except Country.DoesNotExist:
                pass

        self.fields['region'].empty_label = 'Выберите регион'  # type: ignore[attr-defined]
        self.fields['city'].empty_label = 'Выберите город'  # type: ignore[attr-defined]

    def clean_city(self) -> City:
        """
        Проверка корректности заполнения поля 'City'.
        Не допускается создание записей с одинаковыми 'user', 'region', 'city' и 'date_of_visit'.
        """
        city: City = self.cleaned_data['city']
        date_of_visit = self.cleaned_data['date_of_visit']

        # Для того чтобы во время редактирования не проверялось существование аналогичной записи,
        # удаляем её из результатов запроса.
        db_city = VisitedCity.objects.filter(
            user_id=self.request.user,
            # region=self.cleaned_data['region'],
            city=city,
            date_of_visit=date_of_visit,
        ).exclude(id=self.instance.id)

        if db_city.exists():
            raise ValidationError(
                f'Город "{city}" уже был отмечен Вами как посещённый {date_of_visit.strftime("%d.%m.%Y") if date_of_visit else "без указания даты"}'
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

        return str(rating)
