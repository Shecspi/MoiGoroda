from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from place.models import Place
from place.serializers import PlaceSerializer


class CreatePlace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceSerializer


class DeletePlace(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user)
