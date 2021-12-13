from rest_framework import serializers
from news.models import NewsData, PopularKeyword


class NewsSerializers(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%m/%d', read_only=True)

    class Meta:
        model = NewsData
        fields = ("title", "link", "image", "date")


class PopularKeywordSerializers(serializers.ModelSerializer):
    class Meta:
        model = PopularKeyword
        fields = ("word",)
