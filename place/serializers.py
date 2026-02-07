import uuid
from typing import Any

from rest_framework import serializers

from place.models import Place, TagOSM, Category, PlaceCollection


class TagOSMSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = TagOSM
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    tags_detail = TagOSMSerializer(many=True, source='tags', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'tags': {
                'write_only': True,
            }
        }


class PlaceCollectionSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = PlaceCollection
        fields = ('id', 'title', 'is_public', 'user')
        extra_kwargs = {
            'user': {'read_only': True, 'required': False},
        }


class PlaceSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    category_detail = CategorySerializer(source='category', read_only=True)
    collection_detail = PlaceCollectionSerializer(source='collection', read_only=True)

    def _validate_collection_for_user(
        self,
        collection: PlaceCollection | uuid.UUID | str | None,
        user: Any,
    ) -> PlaceCollection | None:
        if collection is None:
            return None
        if isinstance(collection, PlaceCollection):
            if collection.user_id != getattr(user, 'id', user):
                raise serializers.ValidationError(
                    {'collection': 'Коллекция не найдена или недоступна.'}
                )
            return collection
        try:
            return PlaceCollection.objects.get(pk=collection, user=user)
        except PlaceCollection.DoesNotExist:
            raise serializers.ValidationError(
                {'collection': 'Коллекция не найдена или недоступна.'}
            )

    def create(self, validated_data: dict[str, Any]) -> Place:
        """
        Добавляет поле user в сохраняемую модель.
        """
        # Эта немного костыльная проверка нужна для того, чтобы в тестах можно было
        # вызывать сериализатор напрямую, без HTTP-запроса. Соответственно, в таких случаях
        # request.user будет отсутствовать. Поэтому он передаётся напрямую в виде параметра 'user'.
        # Для продакшена это безопасно, так как на этот эндпоинт может попасть только авторизованный пользователь.
        # Соответственно, если неавторизованный пользователь отправит запрос с 'user', то ничего не произойдёт,
        # так как неавторизованных пользователей система не пустит на этот эндпоинт.
        # А если пользователь авторизован и отправит параметр 'user', то этот параметр будет проигнорирован
        # и вместо него подставится значение из request.user.
        if self.context.get('request') and self.context['request'].user:
            user = self.context['request'].user
            if 'user' in validated_data:
                validated_data.pop('user')
            collection_id = validated_data.pop('collection', None)
            validated_data['collection'] = self._validate_collection_for_user(collection_id, user)
            return Place.objects.create(user=user, **validated_data)
        return super(PlaceSerializer, self).create(validated_data)  # type: ignore[no-any-return]

    def update(self, instance: Place, validated_data: dict[str, Any]) -> Place:
        editable_fields = ['name', 'category', 'is_visited', 'collection']
        request = self.context.get('request')
        if 'collection' in validated_data:
            collection_id = validated_data['collection']
            user = request.user if request else instance.user
            validated_data['collection'] = self._validate_collection_for_user(collection_id, user)
        filtered_data = {
            key: value for key, value in validated_data.items() if key in editable_fields
        }
        for field, value in filtered_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    class Meta:
        model = Place
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'category',
            'category_detail',
            'created_at',
            'updated_at',
            'user',
            'is_visited',
            'collection',
            'collection_detail',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'category': {
                'write_only': True,
            },
            'user': {
                'write_only': True,
                'required': False,
            },
            'collection': {
                'write_only': True,
                'required': False,
                'allow_null': True,
            },
        }
