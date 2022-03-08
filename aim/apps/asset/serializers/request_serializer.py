from rest_framework import serializers

from aim.apps.address.models import City, District
from aim.apps.asset.models import AssetType, AssetStatus, Asset


class AssetFilterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, default=None, allow_blank=True)
    asset_type = serializers.PrimaryKeyRelatedField(required=False,
                                                    allow_null=True,
                                                    default=None,
                                                    allow_empty=True,
                                                    queryset=AssetType.objects.all(),
                                                    help_text="The ID of asset type.")
    asset_status = serializers.PrimaryKeyRelatedField(required=False,
                                                      allow_null=True,
                                                      default=None,
                                                      allow_empty=True,
                                                      queryset=AssetStatus.objects.all(),
                                                      help_text="The ID of asset type.")
    city = serializers.PrimaryKeyRelatedField(required=False,
                                              allow_null=True,
                                              default=None,
                                              allow_empty=True,
                                              queryset=City.objects.all(),
                                              help_text="The ID of city.")
    district = serializers.PrimaryKeyRelatedField(required=False,
                                                  allow_null=True,
                                                  default=None,
                                                  allow_empty=True,
                                                  queryset=District.objects.all(),
                                                  help_text="The ID of district.")
    address = serializers.CharField(required=False, allow_null=True, default=None, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, default=None, allow_blank=True)


class AssetCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    asset_type = serializers.PrimaryKeyRelatedField(
        queryset=AssetType.objects.all(), help_text="The ID of asset type.")
    asset_status = serializers.PrimaryKeyRelatedField(
        queryset=AssetStatus.objects.all(), help_text="The ID of asset status")
    city = serializers.PrimaryKeyRelatedField(required=False,
        queryset=City.objects.all(), help_text="The ID of city")
    district = serializers.PrimaryKeyRelatedField(required=False,
        queryset=District.objects.all(), help_text="The ID of district")
    price = serializers.FloatField()
    address = serializers.CharField(required=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AssetUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=False)
    name = serializers.CharField(required=False, allow_null=False)
    asset_type = serializers.PrimaryKeyRelatedField(required=False,
                                                    allow_null=False,
                                                    queryset=AssetType.objects.all(),
                                                    help_text="The ID of asset type.")
    asset_status = serializers.PrimaryKeyRelatedField(required=False,
                                                      allow_null=False,
                                                      queryset=AssetStatus.objects.all(),
                                                      help_text="The ID of asset type.")
    city = serializers.PrimaryKeyRelatedField(required=False,
                                              allow_null=False,
                                              queryset=City.objects.all(),
                                              help_text="The ID of asset type.")
    district = serializers.PrimaryKeyRelatedField(required=False,
                                                  allow_null=False,
                                                  queryset=District.objects.all(),
                                                  help_text="The ID of asset type.")
    price = serializers.FloatField(required=False, allow_null=False)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
