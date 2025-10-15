from rest_framework import serializers
from .models import Region


class RegionSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    title = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'title']

    def get_title(self, obj: Region) -> str:
        return str(obj)


class RegionSearchParamsSerializer(serializers.Serializer):  # type: ignore[type-arg]
    query = serializers.CharField(required=True)
    country = serializers.CharField(required=False)
