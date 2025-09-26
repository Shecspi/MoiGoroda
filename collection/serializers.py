from rest_framework import serializers


class CollectionSearchParamsSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
