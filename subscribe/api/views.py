from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from subscribe.api.serializers import NotificationSerializer


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
