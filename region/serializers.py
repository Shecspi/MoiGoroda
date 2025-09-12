from rest_framework import serializers
from .models import Region


class RegionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'title']

    def get_title(self, obj):
        return str(obj)


class RegionSearchParamsSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    country = serializers.CharField(required=False)
