from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
def save(request):
    try:
        subscription = SubscriptionRequest.model_validate_json(request.body.decode('utf-8'))
    except ValidationError as exc:
        return JsonResponse({'status': 'error', 'exception': exc.json()}, status=400)

    try:
        result = service.save(subscription, request.user.id, request.user.is_superuser)
        return JsonResponse(result)
    except PermissionError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)


@require_POST
@login_required
def delete_subscriber(request):
    try:
        subscription = DeleteSubscriberRequest.model_validate_json(request.body.decode('utf-8'))
    except ValidationError as exc:
        return JsonResponse({'status': 'error', 'exception': exc.json()}, status=400)

    try:
        result = service.delete_subscriber(subscription, request.user.id)
        return JsonResponse(result)
    except PermissionError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({'status': 'forbidden', 'message': str(e)}, status=403)


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    service_class = None

    def get_service(self):
        return self.service_class()

    def list(self, request: Request) -> Response:
        notifications = self.get_service().list_notifications(request.user.id)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({'notifications': serializer.data})

    def partial_update(self, request: Request, pk: int = None) -> Response:
        notification = self.get_service().mark_notification_as_read(request.user.id, pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    def destroy(self, request: Request, pk: int = None) -> Response:
        self.get_service().delete_notification(request.user.id, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
