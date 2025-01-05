from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from place.serializers import PlaceSerializer


class CreatePlace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceSerializer
