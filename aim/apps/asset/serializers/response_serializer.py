from rest_framework import serializers
from aim.apps.asset.models import Asset, AssetType, AssetStatus


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'name', 'asset_status', 'asset_type', 'price', 'address', 'description', 'city', 'district')


class FilterAssetPagationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField()
    previous = serializers.CharField()
    results = AssetSerializer(many=True)


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ('id', 'name', 'code')


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = ('id', 'name', 'code')
