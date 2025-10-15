from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from pydantic import ValidationError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from subscribe.api.serializers import NotificationSerializer
from subscribe.application.services import SubscriptionService
from subscribe.domain.entities import SubscriptionRequest, DeleteSubscriberRequest
from subscribe.infrastructure.django_repository import (
    DjangoUserRepository,
    DjangoShareSettingsRepository,
    DjangoSubscribeRepository,
)

service = SubscriptionService(
    user_repo=DjangoUserRepository(),
    share_settings_repo=DjangoShareSettingsRepository(),
    subscribe_repo=DjangoSubscribeRepository(),
)


@require_POST
@login_required
def save(request: HttpRequest) -> JsonResponse:
    try:
        subscription = SubscriptionRequest.model_validate_json(request.body.decode('utf-8'))
    except ValidationError as exc:
        return JsonResponse({'status': 'error', 'exception': exc.json()}, status=400)

    try:
        user_id = request.user.id if request.user.id is not None else 0
        result = service.save(subscription, user_id, request.user.is_superuser)
        return JsonResponse(result)
    except PermissionError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)


@require_POST
@login_required
def delete_subscriber(request: HttpRequest) -> JsonResponse:
    try:
        subscription = DeleteSubscriberRequest.model_validate_json(request.body.decode('utf-8'))
    except ValidationError as exc:
        return JsonResponse({'status': 'error', 'exception': exc.json()}, status=400)

    try:
        user_id = request.user.id if request.user.id is not None else 0
        result = service.delete_subscriber(subscription, user_id)
        return JsonResponse(result)
    except PermissionError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    service_class: type | None = None

    def get_service(self):  # type: ignore[no-untyped-def]
        return self.service_class()  # type: ignore[misc]

    def list(self, request: Request) -> Response:
        user_id = (
            request.user.id if hasattr(request.user, 'id') and request.user.id is not None else 0
        )
        notifications = self.get_service().list_notifications(user_id)  # type: ignore[no-untyped-call]
        serializer = NotificationSerializer(notifications, many=True)
        return Response({'notifications': serializer.data})

    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        user_id = (
            request.user.id if hasattr(request.user, 'id') and request.user.id is not None else 0
        )
        notification = self.get_service().mark_notification_as_read(user_id, pk)  # type: ignore[no-untyped-call]
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        user_id = (
            request.user.id if hasattr(request.user, 'id') and request.user.id is not None else 0
        )
        self.get_service().delete_notification(user_id, pk)  # type: ignore[no-untyped-call]
        return Response(status=status.HTTP_204_NO_CONTENT)
