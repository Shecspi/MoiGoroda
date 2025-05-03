from django.shortcuts import redirect


def index(request):
    if request.user.is_authenticated:
        return redirect('city-all-list')
    else:
        return redirect('region-all-list')
