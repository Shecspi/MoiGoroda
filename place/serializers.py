from rest_framework import serializers

from place.models import Place, TagOSM, TypeObject


class TagOSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagOSM
        fields = '__all__'


class TypeObjectSerializer(serializers.ModelSerializer):
    tags_detail = TagOSMSerializer(many=True, source='tags', read_only=True)

    class Meta:
        model = TypeObject
        fields = '__all__'
        extra_kwargs = {
            'tags': {
                'write_only': True,
            }
        }


class PlaceSerializer(serializers.ModelSerializer):
    type_object_detail = TypeObjectSerializer(source='type_object', read_only=True)

    class Meta:
        model = Place
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'type_object',
            'type_object_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'type_object': {
                'write_only': True,
            }
        }
