from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers

from accounts.serializers.common_serializers import BoardShowProfileSerializer
from board.models import Board_post, Recommend, Scrap, Reply, Rereply
from board_list.models import Board_list
from board_list.serializers.boardlistbest_serializers import BestBoardListSerializer

from common.permissions import LowWritePriority


# 쿼리 최적화
class BoardPostListRawSqlSerializer(serializers.Serializer):
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
        return {'board_url': obj.board_url, 'board_name': obj.board_name}


# 게시글 디테일 자세히 보기 및 게시글 작성용 serializer
# 게시글 목록 보여주기 위한 Get Serializer
class BoardPostListSerializer(serializers.Serializer):
    # 아이디
    id = serializers.IntegerField(read_only=True)
    # 제목
    title = serializers.CharField(read_only=True)
    # 내용
    body = serializers.CharField(read_only=True)
    # 조회수
    views = serializers.IntegerField(read_only=True)
    # 추천개수
    recommend_count = serializers.IntegerField(read_only=True)
    # 댓글 개수
    reply_count = serializers.IntegerField(read_only=True)
    board_url = BestBoardListSerializer(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.SerializerMethodField(read_only=True)

    # 오늘이면 시간으로 가져오기 00:00 형태
    # 오늘이 아니면 날짜으로 가져오기 00:18 형태
    def get_created_at(self, obj):
        if obj.created_at.date() == timezone.now().date():
            return obj.created_at.strftime('%H:%M')
        else:
            return obj.created_at.strftime('%m/%d')


class BoardSerializer(serializers.ModelSerializer):
    # "익명이"로 가져올지 유저의 정보를 가져올지
    author = serializers.SerializerMethodField(read_only=True)
    # 조회수
    views = serializers.IntegerField(read_only=True)
    # 추천여부
    recommended = serializers.SerializerMethodField()
    # 추천개수
    recommend_count = serializers.SerializerMethodField()
    # 스크랩여부
    scraped = serializers.SerializerMethodField()
    # 스크랩개수
    scrap_count = serializers.SerializerMethodField()
    # 댓글 개수
    reply_count = serializers.SerializerMethodField()
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField()
    # 카테고리 확인 (source 를 이용해서 모델의 fields 정보를 넣을 수 있다!)
    category = serializers.ReadOnlyField(source='category_id.category_name')
    board_url = serializers.CharField()
    # 5글자 초과해서 입력하도록 설정
    body = serializers.CharField(required=True, min_length=6)

    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.DateTimeField(format='%Y/%m/%d %H:%M', read_only=True)

    class Meta:
        model = Board_post
        fields = ('id', 'title', 'body', 'views',
                  'author', 'board_url', 'category',
                  'category_id', 'recommended', 'recommend_count',
                  'scraped', 'scrap_count', 'reply_count',
                  'created_at', 'is_author', 'anonymous')

        extra_kwargs = {
            'category_id': {'write_only': True},
            # 'anonymous': {'write_only': True},
            'board_list': {'write_only': True},
        }

    def create(self, validated_data):
        # 생성 시
        # 해당 게시글에 게시글 만의 카테고리가 아니면 카테고리 저장 안함!!
        category_id_data = validated_data.get('category_id', None)

        # 쿼리 가져오기
        qs = get_object_or_404(Board_list, board_url=validated_data["board_url"])
        if category_id_data:
            if category_id_data in qs.category.all():
                pass
            else:
                validated_data.pop('category_id')

        # 유저의 레벨이 게시판에서 설정한 priority 보다 낮은 경우, Unauthorized 응답을 보냄
        if self.context.get('request').user.level < qs.write_priority:
            raise LowWritePriority
        # board_url 대입하기
        validated_data['board_url'] = qs
        board_post = Board_post.objects.create(**validated_data)
        return board_post

    def update(self, instance, validated_data):
        # 수정 시
        # 해당 게시글에 게시글 만의 카테고리가 아니면 카테고리 저장 안함!!
        # category_id_data = validated_data['category_id']
        category_id_data = validated_data.get('category_id', None)

        # 말머리에 값이 있을 경우
        if category_id_data:
            # 말머리가 게시판에 있을 경우
            if category_id_data in instance.board_url.category.all():
                instance.category_id = validated_data.get('category_id', instance.category_id)
            else:
                instance.category_id = None
        else:
            instance.category_id = None

        # 관리자가 게시글의 게시판을 업데이트 했을 경우
        if self.context.get('request').user.is_superuser:
            qs = get_object_or_404(Board_list, board_url=validated_data["board_url"])
            instance.board_url = qs
            if category_id_data in qs.category.all():
                instance.category_id = validated_data.get('category_id', instance.category_id)
            else:
                instance.category_id = None

        # 내용 수정하기
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.anonymous = validated_data.get('anonymous', instance.anonymous)

        instance.save()
        return instance

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        if obj.anonymous:
            return None
        else:
            return BoardShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 추천 여부
    def get_recommended(self, obj):
        # 회원이 아닐 경우 False
        try:
            recommended = Recommend.objects.filter(
                author=self.context.get('request').user,
                board_post_id=obj.id
            ).exists()
            return recommended
        except:
            return False

    # 추천 개수
    def get_recommend_count(self, obj):
        recommend_count = Recommend.objects.filter(board_post_id=obj.id).count()
        return recommend_count

    # 스크랩 여부
    def get_scraped(self, obj):
        try:
            scraped = Scrap.objects.filter(author=self.context.get('request').user, board_post_id=obj.id).exists()
            return scraped
        except:
            return False

    # 스크랩 개수
    def get_scrap_count(self, obj):
        scrap_count = Scrap.objects.filter(board_post_id=obj.id).count()
        return scrap_count

    # 댓글 개수
    def get_reply_count(self, obj):
        reply_count = Reply.objects.filter(board_post_id=obj.id).count() + Rereply.objects.filter(
            board_post_id=obj.id).count()
        return reply_count

    # 작성자가 로그인 한사람인 경우 (삭제 가능하도록)
    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False


# Raw SQL 용으로 사용 (이건 쿼리가 아니여서 id 속성으로 잘 접근해야함)
# 예로 사용자가 작성자인지 확인하는 is_author 같은 경우
# 특정 게시글 내용 보여주기 위한 Get Serializer
class BoardDetailGetRawSqlSerializer(serializers.Serializer):
    # 아이디
    id = serializers.IntegerField(read_only=True)
    # 제목
    title = serializers.CharField(read_only=True)
    # 내용
    body = serializers.CharField(read_only=True)
    # "익명이"로 가져올지 유저의 정보를 가져올지
    author = serializers.SerializerMethodField(read_only=True)
    # 조회수
    views = serializers.IntegerField(read_only=True)
    # 추천여부
    recommended = serializers.BooleanField(read_only=True)
    # 추천개수
    recommend_count = serializers.IntegerField(read_only=True)
    # 스크랩여부
    scraped = serializers.BooleanField(read_only=True)
    # 스크랩개수
    scrap_count = serializers.IntegerField(read_only=True)
    # 댓글 개수
    reply_count = serializers.IntegerField(read_only=True)
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField(read_only=True)
    # 카테고리 확인 (source 를 이용해서 모델의 fields 정보를 넣을 수 있다!)
    board_url = serializers.CharField(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.DateTimeField(format='%Y/%m/%d %H:%M', read_only=True)

    anonymous = serializers.BooleanField(read_only=True)

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        if obj.anonymous:
            return None
        else:
            request = self.context.get("request")
            if obj.profile_image:
                profile_image = request.build_absolute_uri(obj.profile_image.url)
            else:
                profile_image = None
            return {
                'nickname': obj.nickname,
                'introduction': obj.introduction,
                'profile_image': profile_image
            }

    # 작성자가 로그인 한사람인 경우 (삭제 가능하도록)
    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user.id:
                return True
            else:
                return False
        except:
            return False


# Create Update 사용
# 특정 게시글 내용 보여주기 위한 Get Serializer
class BoardDetailGetSerializer(serializers.Serializer):
    # 아이디
    id = serializers.IntegerField(read_only=True)
    # 제목
    title = serializers.CharField(read_only=True)
    # 내용
    body = serializers.CharField(read_only=True)
    # "익명이"로 가져올지 유저의 정보를 가져올지
    author = serializers.SerializerMethodField(read_only=True)
    # 조회수
    views = serializers.IntegerField(read_only=True)
    # 추천여부
    recommended = serializers.BooleanField(read_only=True)
    # 추천개수
    recommend_count = serializers.IntegerField(read_only=True)
    # 스크랩여부
    scraped = serializers.BooleanField(read_only=True)
    # 스크랩개수
    scrap_count = serializers.IntegerField(read_only=True)
    # 댓글 개수
    reply_count = serializers.IntegerField(read_only=True)
    # 로그인한 사람이 글쓴이 인지
    is_author = serializers.SerializerMethodField(read_only=True)
    board_url = serializers.CharField(read_only=True)
    # 오늘에 따라 시간을 다른 format 가져와야함
    created_at = serializers.DateTimeField(format='%Y/%m/%d %H:%M', read_only=True)

    anonymous = serializers.BooleanField(read_only=True)

    # 익명이 회원 여부
    def get_author(self, obj):
        # 회원이 아닐 경우 False
        if obj.anonymous:
            return None
        else:
            return BoardShowProfileSerializer(obj.author, context={"request": self.context.get('request')}).data

    # 작성자가 로그인 한사람인 경우 (삭제 가능하도록)
    def get_is_author(self, obj):
        try:
            if obj.author == self.context.get('request').user:
                return True
            else:
                return False
        except:
            return False