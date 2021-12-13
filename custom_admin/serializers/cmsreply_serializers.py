from rest_framework import serializers

from board.models import Reply, Rereply, Replyrecommend

from accounts.serializers.common_serializers import ReplyShowProfileSerializer


# 대댓글 가져오기(익명(nickname))
class AdminRereplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Rereply
        fields = (
            'id', 'author', 'board_post_id',
            'reply_id', 'body', 'is_author',
            'anonymous', 'created_at'
        )
        extra_kwargs = {
            'reply_id': {'write_only': True},
            'board_post_id': {'read_only': True},
        }

    # 익명이여도 닉네임 가져옴
    def get_author(self, obj):
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


# 댓글 가져오기 (익명(nickname))
class AdminReplySerializer(serializers.ModelSerializer):
    # username = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField(read_only=True)
    rereply = AdminRereplySerializer(many=True, read_only=True)
    # 추천여부
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'id', 'author', 'board_post_id',
            'body', 'recommended', 'recommend_count',
            'rereply', 'is_author', 'anonymous',
            'created_at'
        )

    #  익명이여도 닉네임 가져옴
    def get_author(self, obj):
        return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 추천 여부
    def get_recommended(self, obj):
        # 회원이 아닐 경우 False로
        try:
            recommended = Replyrecommend.objects.filter(author=self.context.get('request').user, reply_id=obj.id).exists()
            return recommended
        except:
            return False

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = Replyrecommend.objects.filter(reply_id=obj.id).count()
        return recommend_count

    # 작성자가 로그인 한사람인 경우 (삭제 가능하도록)
    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False
