from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def something(request):
    return HttpResponse('Everything is ok :)')
