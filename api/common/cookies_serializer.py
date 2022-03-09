from rest_framework import serializers

class CookiesSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True, default=None)




