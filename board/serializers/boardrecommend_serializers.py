from rest_framework import serializers

from board.models import Recommend, Replyrecommend, Rereplyrecommend, Scrap


# 글 추천
class RecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommend
        fields = ('board_post_id',)


# 댓글 추천 serializer
class ReplyrecommendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Replyrecommend
        fields = ('reply_id',)


# 대댓글 추천 serializer
class RereplyrecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rereplyrecommend
        fields = ('rereply_id',)


# 글 스크랩
class ScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ('board_post_id',)
