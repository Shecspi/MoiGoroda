from django.http import HttpRequest


def get_visited_cities(): ...


def get_visited_cities_by_year(): ...


def get_visited_cities_from_subscriptions(request: HttpRequest): ...


def get_not_visited_cities(): ...
