from rest_framework import serializers

from place.models import Place, TagOSM, Category


class TagOSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagOSM
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    tags_detail = TagOSMSerializer(many=True, source='tags', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'tags': {
                'write_only': True,
            }
        }


class PlaceSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    def create(self, validated_data):
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
            if 'user' in validated_data:
                validated_data.pop('user')
            return Place.objects.create(user=self.context['request'].user, **validated_data)
        return super(PlaceSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # Поля, доступные для редактирования
        editable_fields = ['name', 'category']

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
        }
