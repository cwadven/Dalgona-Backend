from django.utils import timezone
from rest_framework import serializers

from board.models import Board_post

# 쿼리 최적화
from board_list.serializers.boardlistbest_serializers import BestBoardListSerializer


class BestBoardPostListRawSqlSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
    views = serializers.IntegerField(read_only=True)
    # 추천개수
    recommend_count = serializers.IntegerField(read_only=True)
    # 댓글 개수
    reply_count = serializers.IntegerField(read_only=True)
    board_url = serializers.SerializerMethodField(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')

    def get_board_url(self, obj):
        return {'division':obj.division, 'board_url':obj.board_url, 'board_name':obj.board_name}


# 베스트 글 GET serializer
class BestBoardSerializer(serializers.ModelSerializer):
    board_url = BestBoardListSerializer(read_only=True)

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Board_post
        fields = ('id', 'title', 'body', 'board_url', 'created_at',)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')
