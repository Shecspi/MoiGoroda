import json
from enum import StrEnum, auto

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from subscribe.repository import can_subscribe


class Action(StrEnum):
    subscribe = auto()
    unsubscribe = auto()


def is_user_has_permission_to_change_subscription(from_id: int, user_id: int):
    return from_id == user_id


def has_user_allowed_to_subscribe_to_himself(to_id: int):
    return can_subscribe(to_id)


@require_POST
@login_required
def save(request):
    data = json.loads(request.body.decode('utf-8'))
    from_id = data.get('from_id')
    to_id = data.get('to_id')
    action = data.get('action')

    if not is_user_has_permission_to_change_subscription(from_id, request.user.id):
        return JsonResponse(data={'status': 'forbidden'}, status=403)
    if not has_user_allowed_to_subscribe_to_himself(to_id):
        return JsonResponse(data={'status': 'forbidden'}, status=403)

    if action == 'subscribe':
        print(action, from_id, to_id)
        return JsonResponse({'status': 'subscribed'})
    elif action == 'unsubscribe':
        print(action, from_id, to_id)
        return JsonResponse({'status': 'unsubscribed'})
    else:
        return JsonResponse({'status': 'error'})
