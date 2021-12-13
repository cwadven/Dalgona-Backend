from django.utils import timezone
from rest_framework import serializers

from accounts.serializers.common_serializers import ReplyShowProfileSerializer


# 베스트 댓글 GET serializer
class BestReplySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    body = serializers.CharField(read_only=True)
    reply_image = serializers.ImageField(read_only=True)
    # 추천여부
    recommended = serializers.BooleanField(read_only=True)
    # 추천개수
    recommend_count = serializers.IntegerField(read_only=True)
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField(read_only=True)
    anonymous = serializers.BooleanField(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 작성자가 로그인 한사람인 경우 (삭제 가능하도록)
    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 02/09 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')
