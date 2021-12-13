from rest_framework import serializers
from battle.models import *


# 대댓글 추천 Serializer
class VoteBoardRereplyRecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteBoardRereplyRecommend
        fields = ('voteboardrereply_id',)


# 댓글 추천 Serializer
class VoteBoardReplyRecommendSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoteBoardReplyRecommend
        fields = ('voteboardreply_id',)
