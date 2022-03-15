from rest_framework import serializers
from api.models.article import Article
from api.serializers.base import BaseResponseSerializer


class ArticleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Article
        fields = '__all__'


class ArticleResponseSerializer(BaseResponseSerializer):
    data = ArticleSerializer()
