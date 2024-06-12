import json
from enum import StrEnum, auto

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from pydantic import BaseModel, ValidationError

from subscribe.repository import can_subscribe


class Action(StrEnum):
    subscribe = auto()
    unsubscribe = auto()


class SubscriptionRequest(BaseModel):
    from_id: int
    to_id: int
    action: Action


def is_user_has_permission_to_change_subscription(from_id: int, user_id: int):
    return from_id == user_id


def has_user_allowed_to_subscribe_to_himself(to_id: int):
    return can_subscribe(to_id)


@require_POST
@login_required
def save(request):
    json_data = request.body.decode('utf-8')

    try:
        subscription = SubscriptionRequest.model_validate_json(json_data)
    except ValidationError as exc:
        return JsonResponse(data={'status': 'error', 'exception': exc.json()}, status=400)

    if not is_user_has_permission_to_change_subscription(subscription.from_id, request.user.id):
        return JsonResponse(data={'status': 'forbidden'}, status=403)
    if not has_user_allowed_to_subscribe_to_himself(subscription.to_id):
        return JsonResponse(data={'status': 'forbidden'}, status=403)

    if subscription.action == Action.subscribe:
        return JsonResponse({'status': 'subscribed'})
    elif subscription.action == Action.unsubscribe:
        return JsonResponse({'status': 'unsubscribed'})
