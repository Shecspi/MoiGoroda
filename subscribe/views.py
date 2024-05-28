from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required()
def save(request):
    return JsonResponse({'status': 'ok'})
