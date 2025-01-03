from rest_framework import serializers

from place.models import Place, TagOSM, TypeObject


class TagOSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagOSM
        fields = '__all__'


class TypeObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeObject
        fields = '__all__'
        depth = 1


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'latitude', 'longitude', 'type_object', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        depth = 1
