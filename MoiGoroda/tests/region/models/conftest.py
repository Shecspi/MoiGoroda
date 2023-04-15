import pytest

from django.db import transaction

from region.models import Area, Region


@pytest.fixture
def setup_db():
    areas = [
        'Южный федеральный округ',
        'Дальневосточный федеральный округ',
        'Северо-Кавказский федеральный округ'
    ]
    regions = [
        [1, 'Адыгея', 'R', 'RU-AD'],
        [1, 'Краснодарский', 'K', 'RU-KDA'],
        [1, 'Волгоградская', 'O', 'RU-VGG'],
        [1, 'Севастополь', 'G', 'RU-SEV'],
        [2, 'Еврейская', 'AOb', 'RU-YEV'],
        [2, 'Чукотский', 'AOk', 'RU-CHU'],
        [3, 'Чеченская республика', 'R', 'RU-CE']
    ]
    with transaction.atomic():
        for area in areas:
            area = Area.objects.create(
                title=area
            )
            for region in regions:
                if region[0] == area.id:
                    Region.objects.create(
                        area=area,
                        title=region[1],
                        type=region[2],
                        iso3166=region[3]
                    )