from datetime import datetime
from enum import StrEnum, auto

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pydantic import BaseModel, ValidationError
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from services import logger
from subscribe.repository import (
    can_subscribe,
    is_subscribed,
    add_subscription,
    is_user_exists,
    delete_subscription,
    check_subscription,
)
from subscribe.serializers import NotificationSerializer


class Action(StrEnum):
    subscribe = auto()
    unsubscribe = auto()


class SubscriptionRequest(BaseModel):
    from_id: int
    to_id: int
    action: Action


class DeleteSubscriberRequest(BaseModel):
    user_id: int


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
        logger.warning(request, '(Subscription): Attempt to subscribe for another user')
        return JsonResponse(
            data={
                'status': 'forbidden',
                'message': 'Нельзя оформлять подписки за других пользователей',
            },
            status=403,
        )

    if not is_user_exists(subscription.from_id):
        logger.warning(request, '(Subscription): Attempt to subscribe from not exists user')
        return JsonResponse(
            data={'status': 'forbidden', 'message': 'Передан неверный ID пользователя'}, status=403
        )
    if not is_user_exists(subscription.to_id):
        logger.warning(request, '(Subscription): Attempt to subscribe to not exists user')
        return JsonResponse(
            data={'status': 'forbidden', 'message': 'Передан неверный ID пользователя'}, status=403
        )

    if (
        not has_user_allowed_to_subscribe_to_himself(subscription.to_id)
        and not request.user.is_superuser
    ):
        logger.warning(
            request,
            '(Subscription): Attempt to subscribe to a user, who has not allowed subscriptions',
        )
        return JsonResponse(
            data={
                'status': 'forbidden',
                'message': f'Пользователь с ID {subscription.to_id} не разрешил подписываться на него',
            },
            status=403,
        )

    if subscription.action == Action.subscribe:
        if not is_subscribed(subscription.from_id, subscription.to_id):
            add_subscription(subscription.from_id, subscription.to_id)
        logger.info(
            request,
            f'(Subscription): Successful subscription from user #{subscription.from_id} to user #{subscription.to_id}',
        )
        return JsonResponse({'status': 'subscribed'})
    elif subscription.action == Action.unsubscribe:
        if is_subscribed(subscription.from_id, subscription.to_id):
            delete_subscription(subscription.from_id, subscription.to_id)
        logger.info(
            request,
            f'(Subscription): Successful unsubscription from user #{subscription.from_id} to user #{subscription.to_id}',
        )
        return JsonResponse({'status': 'unsubscribed'})


@require_POST
@login_required
@csrf_exempt
def delete_subscriber(request):
    json_data = request.body.decode('utf-8')

    try:
        subscription = DeleteSubscriberRequest.model_validate_json(json_data)
    except ValidationError as exc:
        return JsonResponse(data={'status': 'error', 'exception': exc.json()}, status=400)

    if not is_user_exists(subscription.user_id):
        logger.warning(request, '(Subscription): Attempt to subscribe from not exists user')
        return JsonResponse(
            data={'status': 'forbidden', 'message': 'Передан неверный ID пользователя'},
            status=403,
        )

    if not check_subscription(subscription.user_id, request.user.id):
        logger.warning(
            request,
            f'(Subscription): The user with ID {subscription.user_id} is not subscribed to the user with ID {request.user.id}',
        )
        return JsonResponse(
            data={
                'status': 'forbidden',
                'message': f'Пользователь с ID {subscription.user_id} не подписан на пользователя с ID {request.user.id}',
            },
            status=403,
        )

    delete_subscription(subscription.user_id, request.user.id)
    logger.info(
        request,
        f'(Subscription): The user with ID {subscription.user_id} has been successfully removed from the subscribers of the user with ID {request.user.id}',
    )

    return JsonResponse({'status': 'success'})


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request: Request) -> Response:
        notifications = request.user.notifications.order_by('is_read', '-id')
        serializer = NotificationSerializer(notifications, many=True)

        return Response({'notifications': serializer.data})

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        notification_obj = get_object_or_404(request.user.notifications, id=pk)
        serializer = NotificationSerializer(notification_obj, data=request.data, partial=True)

        if serializer.is_valid():
            if request.data.get('is_read') and not notification_obj.read_at:
                notification_obj.read_at = datetime.now()

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        notification_obj = get_object_or_404(request.user.notifications, id=pk)
        notification_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
