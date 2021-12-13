from rest_framework import serializers
from django.utils import timezone

from battle.models import VoteItem


# 투표 아이템 정보 가져오기
class VoteItemGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    voteboard_id = serializers.ReadOnlyField(source='voteboard_id.id', read_only=True)
    item_name = serializers.CharField(read_only=True)
    item_content = serializers.CharField(read_only=True)
    item_image = serializers.ImageField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)
    is_voted = serializers.BooleanField(read_only=True)


# 투표 아이템 세부 정보 가져오기
class VoteItemGetDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    voteboard_id = serializers.ReadOnlyField(source='voteboard_id.id', read_only=True)
    item_name = serializers.CharField(read_only=True)
    item_content = serializers.CharField(read_only=True)
    item_image = serializers.ImageField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)
    is_voted = serializers.BooleanField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')


# VoteItem 생성
class VoteItemSerializer(serializers.ModelSerializer):
    # 해당 아이템에 투표된 개수
    vote_count = serializers.SerializerMethodField(read_only=True)
    # 해당 아이템 투표여부 확인
    is_voted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteItem
        fields = ('id', 'voteboard_id', 'item_name', 'item_content', 'item_image', 'vote_count', 'is_voted',)

    # 해당 아이템에 투표된 개수 확인
    def get_vote_count(self, obj):
        return obj.vote_set.count()

    # 해당 아이템 투표여부 확인
    def get_is_voted(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.vote_set.filter(voter=self.context.get('request').user).exists()
        else:
            return False


# VoteItem 수정, 삭제(voteboard_id 작성할 필요 없음)
class VoteItemDetailSerializer(serializers.ModelSerializer):
    # 해당 아이템에 투표된 개수
    vote_count = serializers.SerializerMethodField(read_only=True)
    # 해당 아이템 투표여부 확인
    is_voted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteItem
        fields = ('id', 'voteboard_id', 'item_name', 'item_content', 'item_image', 'vote_count', 'is_voted',)
        extra_kwargs = {
            'voteboard_id': {'read_only': True},
        }

    # 해당 아이템에 투표된 개수 확인
    def get_vote_count(self, obj):
        return obj.vote_set.count()

    # 해당 아이템 투표여부 확인
    def get_is_voted(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.vote_set.filter(voter=self.context.get('request').user).exists()
        else:
            return False
