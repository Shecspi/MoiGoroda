from rest_framework import serializers
from .models import Region


class RegionSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    title = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'title', 'country_name']

    def get_title(self, obj: Region) -> str:
        """
        Возвращает полное название региона.

        :param obj: Экземпляр модели Region
        :return: Полное название региона
        """
        return obj.full_name

    def get_country_name(self, obj: Region) -> str:
        """
        Возвращает название страны.

        :param obj: Экземпляр модели Region
        :return: Название страны
        """
        return obj.country.name


class RegionSearchParamsSerializer(serializers.Serializer):  # type: ignore[type-arg]
    query = serializers.CharField(required=True)
    country = serializers.CharField(required=False)
