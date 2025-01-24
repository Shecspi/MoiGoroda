from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from place.models import Place, Category
from place.serializers import PlaceSerializer, CategorySerializer
from services import logger


class GetCategory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            '(API: Place): Getting a list of categories',
        )
        return super(GetCategory, self).get(*args, **kwargs)


class GetPlaces(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = PlaceSerializer

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            '(API: Place): Getting a list of places',
        )
        return super(GetPlaces, self).get(*args, **kwargs)

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user)


class CreatePlace(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceSerializer

    def post(self, *args, **kwargs):
        return super(CreatePlace, self).post(*args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            self.request,
            f'(API: Place): Creation of the place #{instance.id}',
        )


class DeletePlace(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user)

    def delete(self, *args, **kwargs):
        logger.info(
            self.request,
            f'(API: Place): Deleting a place #{self.kwargs["pk"]}',
        )
        return super(DeletePlace, self).delete(*args, **kwargs)
