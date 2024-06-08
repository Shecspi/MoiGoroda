import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
@login_required
def save(request):
    data = json.loads(request.body.decode('utf-8'))
    from_id = data.get('from_id')
    to_id = data.get('to_id')
    action = data.get('action')

    if action == 'subscribe':
        print(action, from_id, to_id)
        return JsonResponse({'status': 'subscribed'})
    elif action == 'unsubscribe':
        print(action, from_id, to_id)
        return JsonResponse({'status': 'unsubscribed'})
    else:
        return JsonResponse({'status': 'error'})
