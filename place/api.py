from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from place.models import Place, TypeObject
from place.serializers import PlaceSerializer, TypeObjectSerializer


class GetTypePlace(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = TypeObjectSerializer
    queryset = TypeObject.objects.all()


class GetPlaces(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = PlaceSerializer

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user)


class CreatePlace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceSerializer


class DeletePlace(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user)
