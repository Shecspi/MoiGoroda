from rest_framework import serializers

from place.models import Place


class CreatePlaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    def create(self, validated_data):
        print(f'\n\n\n\n\n{validated_data}\n\n\n\n\n')
        return Place.objects.create(**validated_data)

    class Meta:
        model = Place
        fields = ['name']
