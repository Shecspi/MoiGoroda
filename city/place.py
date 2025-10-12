from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def place(request: HttpRequest) -> HttpResponse:
    return render(request, 'place/place.html')
