from django.shortcuts import render


def place(request):
    return render(request, 'place/place.html')
