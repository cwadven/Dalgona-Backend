from django.utils import timezone

from rest_framework import serializers

from accounts.serializers.common_serializers import ReplyShowProfileSerializer

from board.models import Rereply, Rereplyrecommend, Reply, Replyrecommend


# 대댓글 조회 serializer
class RereplyGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    body = serializers.CharField(read_only=True)
    rereply_image = serializers.ImageField(read_only=True)
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


# 댓글 조회 serializer
class ReplyGetSerializer(serializers.Serializer):
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

    rereply = RereplyGetSerializer(read_only=True, many=True)

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


# 대댓글 serializer
class RereplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField()
    # 3글자 초과해서 입력하도록 설정
    body = serializers.CharField(required=True, min_length=4)
    # 추천여부
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Rereply
        fields = ('id', 'author', 'body', 'rereply_image', 'reply_id', 'recommended', 'recommend_count',
                  'is_author', 'anonymous', 'created_at')
        extra_kwargs = {
            'reply_id': {'write_only': True},
        }

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

    # 추천 여부
    def get_recommended(self, obj):
        # 회원이 아닐 경우 False
        try:
            recommended = Rereplyrecommend.objects.filter(author=self.context.get('request').user,
                                                          rereply_id=obj.id).exists()
            return recommended
        except:
            return False

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = Rereplyrecommend.objects.filter(rereply_id=obj.id).count()
        return recommend_count

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 02/09 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 대댓글 수정 serializer
class RereplyDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    body = serializers.CharField(required=True, min_length=4)

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Rereply
        fields = ('id', 'author', 'board_post_id', 'reply_id', 'body', 'rereply_image', 'anonymous', 'created_at')

        extra_kwargs = {
            'board_post_id': {'read_only': True},
            'reply_id': {'read_only': True}
        }

    def get_author(self, obj):
        return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 02/09 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 댓글 serializer
class ReplySerializer(serializers.ModelSerializer):
    # username = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField(read_only=True)
    # 3글자 초과해서 입력하도록 설정
    body = serializers.CharField(required=True, min_length=4)
    rereply = RereplySerializer(many=True, read_only=True)
    # 추천여부
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField()

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reply
        fields = ('id', 'author', 'board_post_id',
                  'body', 'reply_image', 'recommended', 'recommend_count',
                  'is_author', 'anonymous', 'created_at', 'rereply',)
        extra_kwargs = {
            'board_post_id': {'write_only': True},
        }

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 추천 여부
    def get_recommended(self, obj):
        # 회원이 아닐 경우 False
        try:
            recommended = Replyrecommend.objects.filter(author=self.context.get('request').user,
                                                        reply_id=obj.id).exists()
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

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 02/09 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 댓글 수정 serializer
class ReplyDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    body = serializers.CharField(required=True, min_length=4)

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reply
        fields = ('id', 'author', 'board_post_id', 'body', 'reply_image', 'anonymous', 'created_at')

        extra_kwargs = {
            'board_post_id': {'read_only': True},
        }

    def get_author(self, obj):
        return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 02/09 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')
