from rest_framework import serializers

from board.serializers.board_serializers import BoardSerializer
from board_list.serializers.boardlist_serializers import CategorySerializer

from board_list.models import Board_list
from accounts.models import Profile


class BoardDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Board_list
        fields = (
            "id", "board_name", "board_url",
            "category", "introduction", "division",
            "write_priority", "read_priority"
        )


class BoardListDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board_list
        fields = (
            "id", "board_name", "board_url",
            "introduction", "division", "created_at",
            "updated_at", "write_priority", "read_priority"
        )


# 게시글에서 관리자 페이지는 username 보이도록
class AdminBoardShowProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    introduction = serializers.CharField(max_length=300, required=False,)
    profile_image = serializers.ImageField(required=False,)

    class Meta:
        model = Profile
        fields = ("username", "nickname", "introduction", "profile_image",)


# 게시글 목록 가져오기(익명(nickname)) 상속으로 가져와서
class AdminBoardSerializer(BoardSerializer):
    # 익명이 익명인 것만 오버라이드
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        return AdminBoardShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

