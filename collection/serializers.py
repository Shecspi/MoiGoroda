from rest_framework import serializers


class CollectionSearchParamsSerializer(serializers.Serializer):  # type: ignore[type-arg]
    query = serializers.CharField(required=True)
