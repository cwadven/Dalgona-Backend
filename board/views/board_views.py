import datetime
from collections import OrderedDict

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Q, Count, Exists
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status, viewsets, renderers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.models import Profile
from board.models import Board_post, Scrap, Recommend
from custom_admin.models import PointLog
from board_list.models import Board_list

from board.serializers.board_serializers import (
    BoardSerializer, BoardPostListRawSqlSerializer, BoardPostListSerializer,
    BoardDetailGetRawSqlSerializer, BoardDetailGetSerializer
)
from board.serializers.boardbest_serializers import BestBoardPostListRawSqlSerializer

from board.raw_sqls import show_board_all_list_raw_query, board_list_all_raw_query

from common.pagination import BasicPagination
from common.permissions import IsOwnerOrSuperUserOrReadOnly, IsPureUser
from common.point_rules import point_check


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 모든 게시판에서 최신글 보기
class NewBoardViewset(generics.ListAPIView):
    queryset = Board_post.objects.select_related('board_url').only(
        'id', 'title', 'created_at', 'board_url__board_url', 'board_url__board_name'
    ).all()
    serializer_class = BoardPostListSerializer
    permission_classes = (AllowAny,)

    # 최신 게시글 보기
    def get(self, request):
        qs = self.get_queryset().order_by('-created_at')[:6]
        serializer = self.get_serializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 모든 게시판에서 글 목록 보기
class BoardPostListAllAPIView(generics.ListAPIView):
    queryset = None
    serializer = None
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    def get(self, request):

        get_data = request.query_params
        # 페이지 네이션
        offset = 0

        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        # SQL RAW 검색 기능 포함 board_url 포함
        qs = show_board_all_list_raw_query(start=offset, limit=18)
        # 개수 세는거 count board 또한 적용
        # * 따로 권한에 따른 게시글 안 가져오도록 분리 못함 이유는 분리하면 가져오는게 너무 느림 **
        if request.user.is_authenticated:
            count_qs = Board_post.objects.select_related('board_url').filter(board_url__read_priority__gte=-1)
        else:
            count_qs = Board_post.objects.select_related('board_url').filter(board_url__read_priority__gte=-1)

        count = count_qs.count()

        serializer = BestBoardPostListRawSqlSerializer(qs, many=True)

        return Response(OrderedDict([('count', count), ('results', serializer.data)]), status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 특정 게시판 글 목록 보기
class BoardPostListAPIView(generics.ListAPIView):
    queryset = Board_post.objects.all()
    serializer = None
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)
    # 페이지 네이션 적용
    pagination_class = BasicPagination

    # 리스트로 쭉 가져오기
    def get(self, request, board_url=None):
        instance = get_object_or_404(Board_list, board_url=board_url)

        # 유저의 레벨이 게시판에서 설정한 priority 낮은 경우, Unauthorized 응답을 보냄
        if isinstance(request.user, AnonymousUser) or request.user.level < instance.read_priority:
            # 모든 사람이 볼 수 있다 -1
            if instance.read_priority > -1:
                return Response({'msg': 'User level is low to read this post'}, status=status.HTTP_401_UNAUTHORIZED)

        get_data = request.query_params

        # 페이지 네이션
        offset = 0

        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        # 정렬은 아직 불가능 속도 너무.. 추천순, 댓글, 조회 순으로 너무 느림
        qs = board_list_all_raw_query(
            request=request,
            start=offset,
            limit=18,
            searchType=get_data.get('searchType'),
            searchWord=get_data.get('searchWord'),
            board_url=board_url,
            ordering=get_data.get('ordering')
        )

        # 개수 세는거 count board 또한 적용
        if request.user.is_authenticated:
            count_qs = Board_post.objects.select_related('board_url').filter(
                board_url__read_priority__lte=request.user.level)
        else:
            count_qs = Board_post.objects.select_related('board_url').filter(board_url__read_priority__lte=-1)

        count_qs = count_qs.filter(board_url__board_url=board_url)

        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                count_qs = count_qs.filter(title__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'body':
                count_qs = count_qs.filter(body__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'title-body':
                count_qs = count_qs.filter(
                    Q(title__contains=get_data.get('searchWord')) | Q(body__contains=get_data.get('searchWord'))
                )

        count = count_qs.count()

        serializer = BoardPostListRawSqlSerializer(qs, many=True)

        return Response(OrderedDict([('count', count), ('results', serializer.data)]), status=status.HTTP_200_OK)


# [쿼리 최적화 완료 (Retrieve 조회, 수정후, 작성후도)]
# [특정 속성만 가져오기 (Retrieve 조회, 수정후, 작성후)]
# 추후에 url 들어오면 해당 url 있는 것으 get 가져오도록 APIVIEW 필요
class BoardViewset(viewsets.ModelViewSet):
    queryset = Board_post.objects.select_related('author', 'board_url').order_by('-created_at')  # id 만큼 가져오기
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)
    # 페이지 네이션 적용
    pagination_class = BasicPagination

    ## 중요 : 이건 custom-admin에서만 이제 이용한다 -> 대체로 위에 있는 BoardPostListAPIView 와 BoardPostAllListAPIView 를 이용한다 ##
    # 전체 게시판에 있는 것들의 조회만 가능
    @action(detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all_boards(self, request, *args, **kwargs):

        # 권한에 맞는 글 가져오기
        if request.user.is_authenticated:
            qs = self.get_queryset().filter(board_url__read_priority__lte=request.user.level)
        else:
            qs = self.get_queryset().filter(board_url__read_priority__lte=-1)

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title, nickname / word : 제목
        # search_type=username&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                qs = qs.filter(title__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'nickname':
                qs = qs.filter(author__nickname__contains=get_data.get('searchWord'))

        # 말머리 필터링 이후 정렬하기
        if get_data.get('category_id'):
            # 말머리 필터링 쿼리 존재 시 필터링하기
            qs = qs.filter(category_id=get_data.get('category_id')) if get_data.get('category_id') is not None else qs

        if get_data.get('ordering'):
            # 정렬할 때 기본으로 views 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
            ordering = "-" + get_data.get('ordering') if get_data.get('ordering') is not None else '-created_at'
            try:
                qs = qs.order_by(ordering, '-created_at')
            except:
                pass

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 리스트로 쭉 가져오기
    def list(self, request, board_url=None):
        instance = get_object_or_404(Board_list, board_url=board_url)

        # 유저의 레벨이 게시판에서 설정한 priority보다 낮은 경우, Unauthorized 응답을 보냄
        if isinstance(request.user, AnonymousUser) or request.user.level < instance.read_priority:
            # 모든 사람이 볼 수 있다 -1
            if instance.read_priority > -1:
                return Response({'msg': 'User level is low to read this post'}, status=status.HTTP_401_UNAUTHORIZED)

        qs = self.get_queryset()

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title, nickname / word : 제목
        # search_type=username&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                qs = qs.filter(title__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'nickname':
                qs = qs.filter(author__nickname__contains=get_data.get('searchWord'))

        # 말머리 필터링 이후 정렬하기
        if get_data.get('category_id'):
            # 말머리 필터링 쿼리 존재 시 필터링하기
            qs = qs.filter(category_id=get_data.get('category_id')) if get_data.get('category_id') is not None else qs

        if get_data.get('ordering'):
            # 정렬할 때 기본으로 views 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
            ordering = "-" + get_data.get('ordering') if get_data.get('ordering') is not None else '-created_at'
            try:
                qs = qs.order_by(ordering, '-created_at')
            except:
                pass

        if board_url:
            # 만약에 파라미터가 있으면 필터
            qs = qs.filter(board_url__board_url=board_url)

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # detail 하나 가져오기
    def retrieve(self, request, board_url=None, pk=None):
        # 한 개의 게시글 가져올 경우
        qs = Profile.objects.raw('''SELECT board_board_post.id,
            board_board_post.created_at,
            board_board_post.board_url_id,
            board_board_post.author_id AS author,
            board_board_post.title,
            board_board_post.body,
            board_board_post.views,
            board_board_post.anonymous,
            (select COUNT(board_recommend.id) FROM board_recommend WHERE board_board_post.id = board_recommend.board_post_id_id) AS recommend_count,
            (select COUNT(board_scrap.id) FROM board_scrap WHERE board_board_post.id = board_scrap.board_post_id_id) AS scrap_count,
            (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(board_rereply.id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count,
            EXISTS(
                SELECT U0.id
                FROM board_scrap U0
                WHERE (U0.author_id = %(author_id)s AND U0.board_post_id_id = %(pk)s)
            ) AS scraped,
            EXISTS(
                SELECT U0.id
                FROM board_recommend U0
                WHERE (U0.author_id = %(author_id)s AND U0.board_post_id_id = %(pk)s)
            ) AS recommended,
            accounts_profile.id,
            accounts_profile.nickname,
            accounts_profile.introduction,
            accounts_profile.profile_image,
            board_list_board_list.id,
            board_list_board_list.board_name,
            board_list_board_list.board_url
            FROM board_board_post
            LEFT OUTER JOIN accounts_profile
            ON board_board_post.author_id = accounts_profile.id
            INNER JOIN board_list_board_list
            ON (board_board_post.board_url_id = board_list_board_list.id)
            WHERE board_list_board_list.board_url = %(board_url)s AND board_board_post.id = %(pk)s''',
                                 {'author_id': request.user.id, 'pk': pk, 'board_url': board_url})

        instance = get_object_or_404(self.get_queryset(), board_url__board_url=board_url, pk=pk)

        # 유저의 레벨이 게시판에서 설정한 priority 보다 낮은 경우, Unauthorized 응답을 보냄
        if isinstance(request.user, AnonymousUser) or request.user.level < instance.board_url.read_priority:
            # 모든 사람이 볼 수 있다 -1
            if instance.board_url.read_priority > -1:
                return Response({'msg': 'User level is low to read this post'}, status=status.HTTP_401_UNAUTHORIZED)

        # 하루 뒤에 초기화
        tomorrow = datetime.datetime.replace(timezone.datetime.now(), hour=23, minute=59, second=0)
        expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")

        # 조회수 증가 (쿠키에 hit 없을 경우 조회수 증가 없앰!)

        if request.COOKIES.get('hit') is not None:
            had_cookies = request.COOKIES.get('hit')
            cookies_list = had_cookies.split('.')
            if str(pk) not in cookies_list:
                with transaction.atomic():
                    instance.views = instance.views + 1
                    instance.save()
        else:
            had_cookies = False
            with transaction.atomic():
                instance.views = instance.views + 1
                instance.save()

        # 조회수가 증가된 후 그 instance serializer 통해서 보여줌
        serializer = BoardDetailGetRawSqlSerializer(qs[0], context={"request": request})
        response = Response(serializer.data, status=status.HTTP_200_OK)

        # 쿠키가 있었을 경우와 없었을 경우를 만듬
        if had_cookies:
            cookies_list = had_cookies.split('.')
            if str(pk) not in cookies_list:
                # secure samesite 직접 설정해줘서 프론트 크롬에서 쿠키를 이용할 수 있도록! (단, HTTPS 백엔드가 돌아가야한다)
                response.set_cookie('hit', had_cookies + f'.{pk}', expires=expires, secure=True, samesite='None')
        else:
            # secure samesite 직접 설정해줘서 프론트 크롬에서 쿠키를 이용할 수 있도록! (단, HTTPS 백엔드가 돌아가야한다)
            response.set_cookie('hit', pk, expires=expires, secure=True, samesite='None')

        return response

    @transaction.atomic
    def perform_create(self, serializer):  # 자동으로 자기 자신 author 저장 되도록
        user = self.request.user
        created = serializer.save(author=user)
        # 해당 유저가 하루에 받은 포인트가 50미만일 경우 포인트 지급, 아니라면 미지급
        point_check(user=user, kind='게시글작성', information="게시글 작성으로 포인트가 추가 되었습니다", points=2, kindid=created.id)
        return created

    @transaction.atomic
    def perform_update(self, serializer):  # 자동으로 자기 자신 author에 저장 되도록:
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.perform_create(serializer)

        # 생성 후 쿼리 조회를 하는 최적화
        qs = self.get_queryset().annotate(
            recommend_count=Count('recommend', distinct=True)
        ).annotate(
            scrap_count=Count('scrap', distinct=True)
        ).annotate(
            reply_count=Count('reply', distinct=True) + Count('rereply', distinct=True)
        ).annotate(
            scraped=Exists(
                Scrap.objects.only('id').filter(
                    author=(request.user if request.user.is_authenticated else None),
                    board_post_id=result.id
                )
            )
        ).annotate(
            recommended=Exists(
                Recommend.objects.only('id').filter(
                    author=(request.user if request.user.is_authenticated else None),
                    board_post_id=result.id
                )
            )
        ).only(
            'id', 'title', 'body',
            'views', 'author', 'created_at',
            'anonymous', 'board_url', 'author',
            'author__nickname', 'author__introduction',
            'author__profile_image', 'board_url__board_url'
        )

        instance = get_object_or_404(qs, board_url__board_url=result.board_url, pk=result.id)

        serializer = BoardDetailGetSerializer(instance, context={"request": request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 만약 인기게시글이 됐을 경우 수정 못하게 막음
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # 만약 인기게시글이 됐을 경우 수정 못하게 막음
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if PointLog.objects.filter(kind='특정게시판인기게시글', kindid=instance.id).exists():
            return Response(
                {"result": "인기게시글이 되었던 적 있는 게시글로 수정이 불가능 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        # 수정 후 쿼리 조회를 하는 최적화
        qs = self.get_queryset().annotate(
            recommend_count=Count('recommend', distinct=True)
        ).annotate(
            scrap_count=Count('scrap', distinct=True)
        ).annotate(
            reply_count=Count('reply', distinct=True) + Count('rereply', distinct=True)
        ).annotate(
            scraped=Exists(
                Scrap.objects.only('id').filter(
                    author=(request.user if request.user.is_authenticated else None),
                    board_post_id=instance.id
                )
            )
        ).annotate(
            recommended=Exists(
                Recommend.objects.only('id').filter(
                    author=(request.user if request.user.is_authenticated else None),
                    board_post_id=instance.id
                )
            )
        ).only(
            'id', 'title', 'body',
            'views', 'author', 'created_at',
            'anonymous', 'board_url', 'author',
            'author__nickname', 'author__introduction',
            'author__profile_image', 'board_url__board_url'
        )

        instance = get_object_or_404(qs, board_url__board_url=instance.board_url, pk=instance.id)

        serializer = BoardDetailGetSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])

        # 관리자가 삭제했는지 혹은 유저가 삭제했는지
        if self.request.user.is_superuser:
            if PointLog.objects.filter(kind='특정게시판인기게시글', kindid=instance.id).exists():
                PointLog.objects.create(
                    userid=instance.author,
                    kind="인기게시글삭제",
                    information="관리자의 인기게시글 삭제로 받은 포인트가 회수됩니다.",
                    points=15,
                    param='D',
                    kindid=kwargs['pk']
                )

            # 게시글 삭제시 포인트 차감
            PointLog.objects.create(
                userid=instance.author,
                kind="게시글삭제",
                information="관리자의 게시글 삭제로 받은 포인트가 회수됩니다.",
                points=2,
                param='D',
                kindid=kwargs['pk']
            )
        else:
            # 일반 게시글 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함
            if self.request.user.points - 2 < 0:
                return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

            # 인기 게시글 삭제 시 포인트 ?? 회수
            if PointLog.objects.filter(kind='특정게시판인기게시글', kindid=instance.id).exists():
                # 인기 게시글 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함(게시글 포인트 + 인기게시글 포인트)
                if self.request.user.points - 17 < 0:
                    return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

                PointLog.objects.create(
                    userid=instance.author,
                    kind="인기게시글삭제",
                    information="인기게시글 삭제로 받은 포인트가 회수됩니다.",
                    points=15,
                    param='D',
                    kindid=kwargs['pk']
                )

            # 게시글 삭제시 포인트 차감
            PointLog.objects.create(
                userid=instance.author,
                kind="게시글삭제",
                information="게시글 삭제로 받은 포인트가 회수됩니다.",
                points=2,
                param='D',
                kindid=kwargs['pk']
            )
        return super(BoardViewset, self).destroy(request, *args, **kwargs)


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 검색 API 용 -> 큰 게시판(전체, 루나, 자유)마다 다르게 검색 결과를 가져와야 함
class SearchViewset(generics.ListAPIView):
    queryset = Board_post.objects.annotate(
        recommend_count=Count('recommend', distinct=True),
        reply_count=Count('reply', filter=Q(reply__author_id__isnull=False), distinct=True) + Count('rereply',
                                                                                                    distinct=True)
    ).select_related('board_url').only(
        'id', 'title', 'body', 'views', 'board_url', 'created_at',
        'board_url__board_url', 'board_url__board_name',
    ).order_by(
        '-created_at'
    )  # id 만큼 가져오기
    serializer_class = BoardPostListSerializer
    permission_classes = (AllowAny,)
    # 페이지 네이션 적용
    pagination_class = BasicPagination

    # 리스트로 쭉 가져오기
    def get(self, request):
        qs = self.get_queryset()

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title, body, title+body, (nickname) / word : 제목, 내용, 제목+내용
        # search_type=title_body&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchDivision') in ['all', 'free', 'luna', 'dalgona']:
                if get_data.get('searchType') == 'title':
                    qs = qs.filter(title__contains=get_data.get('searchWord'))
                elif get_data.get('serachType') == 'body':
                    qs = qs.filter(body__contains=get_data.get('searchWord'))
                elif get_data.get('searchType') == 'title-body':
                    qs = qs.filter(
                        Q(title__contains=get_data.get('searchWord')) | Q(body__contains=get_data.get('searchWord')))

                if get_data.get('searchDivision') == 'all':  # 전체
                    pass
                elif get_data.get('searchDivision') == 'free':  # 루나
                    qs = qs.filter(board_url__division=1)
                elif get_data.get('searchDivision') == 'luna':  # 자유
                    qs = qs.filter(board_url__division=2)
                # 공지사항 필요 여부 확인
                elif get_data.get('searchDivision') == 'dalgona':
                    qs = qs.filter(board_url__division=0)
            else:
                return Response({"result": "searchDivision query error"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"result": "searchType or searchWord query error"}, status=status.HTTP_400_BAD_REQUEST)

        if get_data.get('ordering'):
            # 정렬할 때 기본으로 views를 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
            ordering = "-" + get_data.get('ordering') if get_data.get('ordering') is not None else '-created_at'
            try:
                qs = qs.order_by(ordering, '-created_at')
            except:
                pass

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
