from rest_framework import serializers


class ArticleCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
