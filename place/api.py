from rest_framework import generics
import rest_framework.exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from place.serializers import CreatePlaceSerializer


class CreatePlace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = CreatePlaceSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreatePlaceSerializer(
            data={'nam1e': 'hello'}, context={'request': self.request}
        )
        if not serializer.is_valid():
            print(f'\n\n\n\n\n\{serializer.errors}\n\n\n\n\n')
            raise drf_exc.ValidationError(serializer.errors)

        serializer.save(name='hello')

        return Response()
