"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django import forms
from django.forms import ModelForm

from collection.models import PersonalCollection
from city.models import City
from country.models import Country
from region.models import Region


class PersonalCollectionCreateForm(forms.Form):
    """
    Форма для создания персональной коллекции городов.
    """

    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(city__isnull=False).distinct().order_by('name'),
        required=False,
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
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label='Выберите город',
        label='Город',
        help_text='Выберите город',
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)

        # По-умолчанию список городов пустой, пока не будет выбран регион
        if not self.errors:
            self.fields['city'].queryset = City.objects.none()  # type: ignore[attr-defined]

        # Код ниже необходим для корректной обработки формы после подгрузки списка городов
        if 'region' in self.data:
            region_id_str = self.data.get('region')
            if region_id_str:
                try:
                    region_id = int(region_id_str)
                    self.fields['city'].queryset = City.objects.filter(  # type: ignore[attr-defined]
                        region_id=region_id
                    ).order_by('title')
                except (ValueError, TypeError):
                    pass
