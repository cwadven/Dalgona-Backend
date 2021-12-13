from rest_framework import serializers

from battle.models import VoteItem


# 실시간 이슈 배틀 아이템 세부 정보 가져오기
class BestVoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteItem
        fields = ('id', 'item_image')


# 실시간 이슈 배틀 게시판 정보 가져오기
class BestVoteBoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    voteitem = BestVoteItemSerializer(read_only=True, many=True)
    vote_count = serializers.IntegerField(read_only=True)
