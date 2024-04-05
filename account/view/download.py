from dataclasses import dataclass
from datetime import datetime
from io import StringIO

from django.http import HttpResponse

from services.db.visited_city_repo import get_all_visited_cities


@dataclass
class CityDataclass:
    title: str
    region: str
    date_of_visit: datetime.date
    has_magnet: bool
    rating: int

    def __str__(self):
        return (
            f'{self.title:<30}'
            f'{str(self.region):<40}'
            f'{"Не указана" if not self.date_of_visit else str(self.date_of_visit):<20}'
            f'{"+" if self.has_magnet else "-":<20}'
            f'{"*" * self.rating:<10}\n'
        )


def serialize_queryset_to_file(request):
    s = StringIO()
    s.write(
        f"{str('Город'):<30}"
        f"{str('Регион'):<40}"
        f'{str('Дата посещения'):<20}'
        f'{str('Наличие магнита'):<20}'
        f'{str('Оценка'):<10}\n\n'
    )
    for city in get_prepared_visited_city_for_download(1):
        s.write(str(city))

    return s.getvalue()


def get_prepared_visited_city_for_download(user_id: int):
    cities = get_all_visited_cities(1)
    result = []
    for city in cities:
        result.append(
            CityDataclass(
                title=city.city.title,
                region=str(city.region),
                date_of_visit=city.date_of_visit,
                has_magnet=city.has_magnet,
                rating=city.rating
            )
        )
    return result


def download(request):
    if request.method == 'POST':
        users_data = request.POST.dict()
        filetype = users_data.get('')

    download_file = serialize_queryset_to_file(request)
    response = HttpResponse(download_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=myfile.txt'
    return response
