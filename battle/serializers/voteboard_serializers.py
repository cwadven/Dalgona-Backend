from django.utils import timezone

from rest_framework import serializers

from battle.models import VoteBoard, VoteBoardReply, VoteBoardRereply
from battle.serializers.voteboarditem_serializers import VoteItemSerializer, VoteItemGetSerializer


# 투표 게시판 리스트 가져오기
class VoteBoardGetListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)
    board_image = serializers.ImageField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True) # 전체 투표 개수
    reply_count = serializers.IntegerField(read_only=True) # 댓글 개수
    is_voted = serializers.BooleanField(read_only=True) # 투표여부 확인
    deadline = serializers.SerializerMethodField(read_only=True)
    is_ended = serializers.SerializerMethodField(read_only=True)

    start_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')
    end_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')

    def get_deadline(self, obj):
        _deadline = obj.end_datetime - timezone.now()
        if obj.end_datetime <= timezone.now():
            return 0
        else:
            return _deadline.days

    def get_is_ended(self, obj):
        if obj.end_datetime >= timezone.now():
            return False
        else:
            return True


class VoteBoardListSerializer(serializers.ModelSerializer):
    # 전체 투표 개수
    vote_count = serializers.SerializerMethodField(read_only=True)
    # 투표여부 확인
    is_voted = serializers.SerializerMethodField(read_only=True)

    deadline = serializers.SerializerMethodField(read_only=True)
    is_ended = serializers.BooleanField(read_only=True, default=False)

    reply_count = serializers.IntegerField(read_only=True, default=0)

    # 오늘에 따라 시간을 다른 format으로 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    voteitem = VoteItemGetSerializer(read_only=True, many=True)

    start_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')
    end_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    class Meta:
        model = VoteBoard
        fields = (
        'id', 'title', 'content', 'board_image', 'vote_count', 'reply_count', 'is_voted', 'deadline', 'is_ended',
        'start_datetime', 'end_datetime', 'created_at', 'voteitem')

    # 전체 투표 개수 확인
    def get_vote_count(self, obj):
        return obj.vote_set.count()

    # 투표여부 확인
    def get_is_voted(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.vote_set.filter(voter=self.context.get('request').user).exists()
        else:
            return False

    def get_deadline(self, obj):
        _deadline = obj.end_datetime - timezone.now()
        if obj.end_datetime <= timezone.now():
            return 0
        else:
            return _deadline.days

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜 으로 가져오기 02/03 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')


# 특정 투표 게시판 정보를 가져올 때, 각 투표 아이템의 투표 수와 사용자가 투표했는지를 나타내기 위함
# 투표 게시판 전체 투표 수와는 다른 것
# 위의 VoteItemGetSerializer 상속받고 vote_count와 is_voted 오버라이딩
class VoteBoardDetailVoteItemGetSerializer(VoteItemGetSerializer):
    vote_count = serializers.SerializerMethodField(read_only=True)
    is_voted = serializers.SerializerMethodField(read_only=True)

    def get_vote_count(self, obj):
        return obj.vote_set.count()

    def get_is_voted(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.vote_set.filter(voter=self.context.get('request').user).exists()
        else:
            return False


# 투표 정보 및 투표율 가져오기
class VoteBoardGetDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)
    board_image = serializers.ImageField(read_only=True)

    vote_count = serializers.IntegerField(read_only=True)  # 투표 게시판 전체 투표 개수
    reply_count = serializers.IntegerField(read_only=True)

    is_voted = serializers.BooleanField(read_only=True)  # 투표 게시판 투표여부 확인
    deadline = serializers.SerializerMethodField(read_only=True)
    is_ended = serializers.SerializerMethodField(read_only=True)

    start_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')
    end_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    created_at = serializers.SerializerMethodField(read_only=True)

    # 각 투표 아이템 정보
    voteitem = VoteBoardDetailVoteItemGetSerializer(read_only=True, many=True)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')

    def get_deadline(self, obj):
        _deadline = obj.end_datetime - timezone.now()
        if obj.end_datetime <= timezone.now():
            return 0
        else:
            return _deadline.days

    def get_is_ended(self, obj):
        if obj.end_datetime >= timezone.now():
            return False
        else:
            return True


# 투표 정보 수정, 삭제
class VoteBoardDetailSerializer(serializers.ModelSerializer):
    # 전체 투표 개수
    vote_count = serializers.SerializerMethodField(read_only=True)
    # 투표여부 확인
    is_voted = serializers.SerializerMethodField(read_only=True)

    # 역참조로 가져오고 있는 voteitem Serializer
    # 이렇게 해야 put 할 때 오류나지 않음 <-> SerializerMethodField 사용시 json parsing 에러 발생
    voteitem = VoteItemSerializer(read_only=True, many=True)
    # voteitem = serializers.SerializerMethodField(read_only=True, many=True)

    # 댓글 개수
    reply_count = serializers.SerializerMethodField()
    # 마감 일자 확인
    deadline = serializers.SerializerMethodField(read_only=True)
    is_ended = serializers.SerializerMethodField(read_only=True)

    # 시작 시간 2021/01/01 10:00 형태로 변경
    start_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')
    # 종료 시간 2021/01/01 10:00 형태로 변경
    end_datetime = serializers.DateTimeField(format='%Y/%m/%d %H:%M')

    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoteBoard
        fields = ('id', 'title', 'content', 'board_image',
                  'vote_count', 'reply_count', 'is_voted', 'deadline', 'is_ended',
                  'start_datetime', 'end_datetime', 'created_at', 'voteitem',)

    # 전체 투표 개수 확인
    def get_vote_count(self, obj):
        return obj.vote_set.count()

    # 투표여부 확인
    def get_is_voted(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.vote_set.filter(voter=self.context.get('request').user).exists()
        else:
            return False

    # 댓글 개수
    def get_reply_count(self, obj):
        reply_count = VoteBoardReply.objects.filter(voteboard_id=obj.id).count() + \
                      VoteBoardRereply.objects.filter(voteboard_id=obj.id).count()
        return reply_count

    def get_deadline(self, obj):
        _deadline = obj.end_datetime - timezone.now()
        if obj.end_datetime <= timezone.now():
            return 0
        else:
            return _deadline.days

    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')

    def get_is_ended(self, obj):
        if obj.end_datetime >= timezone.now():
            return False
        else:
            return True