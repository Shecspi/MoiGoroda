from rest_framework import serializers


class CollectionSearchParamsSerializer(serializers.Serializer):  # type: ignore[type-arg]
    query = serializers.CharField(required=True)


class PersonalCollectionCreateSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """
    Сериализатор для создания персональной коллекции.
    """

    title = serializers.CharField(required=True, max_length=256)
    city_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
    is_public = serializers.BooleanField(required=False, default=False)


class PersonalCollectionUpdatePublicStatusSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """
    Сериализатор для изменения статуса публичности персональной коллекции.
    """

    is_public = serializers.BooleanField(required=True)


class PersonalCollectionUpdateSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """
    Сериализатор для обновления персональной коллекции.
    """

    title = serializers.CharField(required=True, max_length=256)
    city_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
    is_public = serializers.BooleanField(required=False, default=False)
