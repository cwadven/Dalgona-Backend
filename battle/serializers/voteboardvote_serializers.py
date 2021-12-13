from rest_framework import serializers

from battle.models import Vote


# 투표 Serializer
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'voteitem_id', 'created_at', 'updated_at')
