from rest_framework import serializers
from django.utils import timezone
from accounts.serializers.common_serializers import ReplyShowProfileSerializer

from battle.models import VoteBoardRereply, VoteBoardRereplyRecommend, VoteBoardReply, VoteBoardReplyRecommend


# 대댓글 정보 가져오기
class VoteRereplyGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    content = serializers.CharField(read_only=True)
    voterereply_image = serializers.ImageField(read_only=True)
    recommended = serializers.BooleanField(read_only=True)
    recommend_count = serializers.IntegerField(read_only=True)
    is_author = serializers.SerializerMethodField(read_only=True)
    anonymous = serializers.BooleanField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')
            # 익명이 회원 여부

    def get_author(self, obj):
        # 회원이 아닐 경우 False로
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


# 대댓글 작성 및 조회 Serializer
class VoteRereplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 3자 초과해서 입력하도록 설정
    content = serializers.CharField(required=True, min_length=4)
    is_author = serializers.SerializerMethodField()
    # 추천 여부
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()

    # 오늘에 따라 시간을 다른 format으로 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteBoardRereply
        fields = ('id', 'voteboardreply_id', 'author', 'content', 'voterereply_image', 'is_author',
                    'recommended', 'recommend_count', 'anonymous', 'created_at')

        extra_kwargs = {
            'voteboardreply_id': {'write_only': True},
        }

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False로
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False

    def get_recommended(self, obj):
        # 회원이 아닐 경우 False로
        try:
            recommended = VoteBoardRereplyRecommend.objects.filter(author=self.context.get('request').user, voteboardrereply_id=obj.id).exists()
            return recommended
        except:
            return False

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = VoteBoardRereplyRecommend.objects.filter(voteboardrereply_id=obj.id).count()
        return recommend_count

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜 + 시간으로 가져오기 02/03 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 대댓글 수정 및 삭제 Serializer
class VoteRereplyDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 3자 초과해서 입력하도록 설정
    content = serializers.CharField(required=True, min_length=4)

    # 오늘에 따라 시간을 다른 format으로 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteBoardRereply
        fields = ('id', 'author', 'content', 'voterereply_image', 'anonymous', 'created_at')

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False로
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜 + 시간으로 가져오기 02/03 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 댓글 정보 가져오기 (특정 게시글 댓글 조회 : 리스트로 가져오기)
class VoteReplyGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    content = serializers.CharField(read_only=True)
    votereply_image = serializers.ImageField(read_only=True)
    is_author = serializers.SerializerMethodField(read_only=True)
    recommended = serializers.BooleanField(read_only=True)
    recommend_count = serializers.IntegerField(read_only=True)
    anonymous = serializers.BooleanField(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)
    voteboardrereply = VoteRereplyGetSerializer(read_only=True, many=True)

    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')

    def get_author(self, obj):
        # 회원이 아닐 경우 False로
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


# 댓글 조회 및 작성 Serializer
class VoteReplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 3자 초과해서 입력하도록 설정
    content = serializers.CharField(required=True, min_length=4)
    voteboardrereply = VoteRereplySerializer(many=True, read_only=True)
    is_author = serializers.SerializerMethodField()
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()

    # 오늘에 따라 시간을 다른 format으로 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteBoardReply
        fields = ('id', 'voteboard_id', 'author', 'content', 'votereply_image', 'is_author',
                'recommended', 'recommend_count', 'anonymous', 'created_at', 'voteboardrereply')

        extra_kwargs = {
            'voteboard_id': {'write_only': True},
        }

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False로
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False

    def get_recommended(self, obj):
        # 회원이 아닐 경우 False로
        try:
            recommended = VoteBoardReplyRecommend.objects.filter(author=self.context.get('request').user, voteboardreply_id=obj.id).exists()
            return recommended
        except:
            return False

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = VoteBoardReplyRecommend.objects.filter(voteboardreply_id=obj.id).count()
        return recommend_count

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜 + 시간으로 가져오기 02/03 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')


# 댓글 수정 및 삭제 Serializer
class VoteReplyDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    # 최소 4글자 이상 입력하도록 설정
    content = serializers.CharField(required=True, min_length=4)

    # 오늘에 따라 시간을 다른 format으로 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteBoardReply
        fields = ('id', 'author', 'content', 'votereply_image', 'anonymous', 'created_at')

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False로
        if obj.anonymous:
            return None
        else:
            return ReplyShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜 + 시간으로 가져오기 02/03 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d %H:%M')
