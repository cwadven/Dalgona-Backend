# 사용자 활동 내역 게시물
from rest_framework import serializers

from board.models import (
    Board_post, Recommend, Scrap,
    Reply, Replyrecommend, Rereply
)


class AccountActivityBoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()
    recommend_count = serializers.SerializerMethodField()
    scrap_count = serializers.SerializerMethodField()

    class Meta:
        model = Board_post
        fields = ("id", "board_name", "title", "body", "recommend_count", "scrap_count", "author", "created_at")

    # 작성자 닉네임
    def get_author(self, obj):
        return obj.author.nickname

    # 게시판 이름
    def get_board_name(self, obj):
        return obj.board_url.board_name

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = Recommend.objects.filter(board_post_id=obj.id).count()
        return recommend_count

    # 스크랩 개수
    def get_scrap_count(self, obj):
        scrap_count = Scrap.objects.filter(board_post_id=obj.id).count()
        return scrap_count


# 사용자 활동 내역 댓글
class AccountActivityReplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()
    recommend_count = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ("id", "board_name", "body", "recommend_count", "author", "created_at",)

    # 작성자 닉네임
    def get_author(self, obj):
        return obj.author.nickname

    # 게시판 이름
    def get_board_name(self, obj):
        return obj.board_post_id.board_url.board_name

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = Replyrecommend.objects.filter(id=obj.id).count()
        return recommend_count


# 사용자 활동 내역 대댓글
class AccountActivityRereplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()

    class Meta:
        model = Rereply
        fields = ("id", "board_name", "body", "author", "created_at",)

    # 작성자 닉네임
    def get_author(self, obj):
        return obj.author.nickname

    # 게시판 이름
    def get_board_name(self, obj):
        return obj.board_post_id.board_url.board_name


# 사용자 활동 내역 스크랩한 글
class AccountActivityScrapSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Scrap
        fields = ("id", "board_name", "title", "author", "created_at",)

    # 작성자 닉네임
    def get_author(self, obj):
        return obj.author.nickname

    def get_title(self, obj):
        return obj.board_post_id.title

    # 게시판 이름
    def get_board_name(self, obj):
        return obj.board_post_id.board_url.board_name