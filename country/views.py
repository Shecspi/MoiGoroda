from django.http import HttpResponse


def country(request):
    return HttpResponse("Hello, world. You're at the country view.")
