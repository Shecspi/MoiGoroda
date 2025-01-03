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


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['name', 'latitude', 'longitude', 'type_object']
