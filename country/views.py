from django.shortcuts import render


def country(request):
    return render(request, 'country/map.html')
