import datetime
from collections import OrderedDict

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status

from board_list.models import Board_list
from accounts.models import Profile
from accounts.serializers.mypage_serializers import (
    SuperBasicProfileUpdateSerializer, BasicProfileUpdateSerializer,
    GetBookmarkSerializer, PostBookmarkSerializer, ScoreSerializer,
    MyPageSerializer, MyBoardSerializer, MyReplySerializer, MyreReplySerializer,
)
from accounts.raw_sqls import my_post_list_raw_query, my_reply_list_raw_query, my_rereply_list_raw_query, point_raw_query

from board.models import Board_post, Reply, Rereply

from custom_admin.models import PointLog
from common.permissions import IsPureUser


# [쿼리 최적화 get delete 완료 / put 확인 불가(?): debug toolbar 사라짐]
# 기본 회원정보 수정할 것
class BasicUpdateView(generics.RetrieveUpdateDestroyAPIView):
    # 로그인 한 사람만 접근 가능
    queryset = Profile.objects.all()
    serializer_class = BasicProfileUpdateSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    # 회원 정보 조회 / JWT 필요
    def get(self, request):
        # 관리자일 경우
        if request.user.is_superuser:
            serializer = SuperBasicProfileUpdateSerializer(request.user, context={"request": request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = BasicProfileUpdateSerializer(request.user, context={"request": request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 회원 정보 수정
    def put(self, request):
        # 기존의 경우
        serializer = self.get_serializer(request.user, data=request.data, context={"request": request}, )
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원 탈퇴
    def delete(self, request):
        try:
            request.user.delete()
            return Response(data={"detail": "user deleted"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(data={"detail": "something get wrong"}, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 get 완료 / post 완료(확인 필요)]
# 즐겨 찾기
class BookmarkView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = GetBookmarkSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    # 회원 즐겨찾기(북마크) 가져오기
    def get(self, request):
        serializer = self.get_serializer(
            request.user, context={"request": request}
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 회원 즐겨찾기(북마크) 추가 및 삭제
    def post(self, request, format=None):
        serializer = PostBookmarkSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # 북마크가 있을 경우와 없을 경우 만들기
            # views 특정 구역 설정해서 수정하는 방식으로 가져오기
            board_list_id = get_object_or_404(Board_list, board_url=serializer.validated_data["bookmark"])
            if board_list_id in request.user.bookmark.all():
                # 추가할 때 하나씩 추가함! 그런데 ManytoManyField 리스트 느낌이여서 안에 있는것을 사용
                request.user.bookmark.remove(board_list_id.id)
                request.user.save()
            else:
                request.user.bookmark.add(board_list_id.id)
                request.user.save()

            # 넣었을 경우 ManytoManyField 안의 모든 내용 보이도록 GetBookmarkSerializer 사용
            get_serializer = self.get_serializer(request.user, context={"request": request})
            return Response(data=get_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
# 내가 쓴 모든 글 가져오기
class MyPostView(generics.ListCreateAPIView):
    queryset = Board_post.objects.all()  # Profile 대신 Board_post 사용
    serializer_class = MyBoardSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = my_post_list_raw_query(request=request, start=offset, limit=18)

        # count 하기
        count_qs = Board_post.objects.select_related('board_url').filter(author=request.user)
        count = count_qs.count()

        serializer = MyBoardSerializer(qs, many=True)

        return Response(OrderedDict([('count', count), ('results', serializer.data)]), status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# 내가 쓴 모든 댓글 가져오기
class MyReplyView(generics.ListCreateAPIView):
    queryset = Reply.objects.select_related('board_post_id', 'author').all()
    serializer_class = MyReplySerializer  # get_serializer 저장
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = my_reply_list_raw_query(request=request, start=offset, limit=18)

        # count 하기
        count_qs = Reply.objects.select_related('board_url').filter(author=request.user)
        count = count_qs.count()

        serializer = MyReplySerializer(qs, many=True)
        return Response(OrderedDict([('count', count), ('results', serializer.data)]), status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# 내가 쓴 모든 대댓글 가져오기
class MyRereplyView(generics.ListCreateAPIView):
    queryset = Rereply.objects.select_related('reply_id', 'author').all()
    # get_serializer 저장
    serializer_class = MyreReplySerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = my_rereply_list_raw_query(request=request, start=offset, limit=18)
        serializer = MyreReplySerializer(qs, many=True)

        # count 하기
        count_qs = Rereply.objects.select_related('board_url, reply').filter(author=request.user)
        count = count_qs.count()

        return Response(OrderedDict([('count', count), ('results', serializer.data)]), status=status.HTTP_200_OK)


# [쿼리 최적화 불필요]
# 어떤 사람이 많이 쓰거나 했는지
class ScoreView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = (AllowAny,)

    def get(self, request):

        # 정렬하기
        get_data = request.query_params

        # 날짜 기준으로 필터링
        # 선택한 날짜 것들만 개수 가져오기
        try:
            if get_data['date']:
                selected_date = datetime.datetime.strptime(get_data['date'] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                qs = self.get_queryset().annotate(
                    board_write=Count('board_post', distinct=True, filter=Q(
                        board_post__created_at__gte=selected_date,
                        board_post__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                      ),
                    reply_write=Count('reply', distinct=True, filter=Q(
                        reply__created_at__gte=selected_date,
                        reply__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                      ),
                    rereply_write=Count('rereply', distinct=True, filter=Q(
                        rereply__created_at__gte=selected_date,
                        rereply__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                        ),
                    total=Count('board_post', distinct=True, filter=Q(
                        board_post__created_at__gte=selected_date,
                        board_post__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                ) + Count('reply', distinct=True, filter=Q(
                        reply__created_at__gte=selected_date,
                        reply__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                          ) + Count('rereply', distinct=True, filter=Q(
                        rereply__created_at__gte=selected_date,
                        rereply__created_at__lte=selected_date + datetime.timedelta(days=1)
                    )
                                                    )
                )
        except Exception as e:
            qs = self.get_queryset().annotate(
                board_write=Count('board_post', distinct=True),
                reply_write=Count('reply', distinct=True),
                rereply_write=Count('rereply', distinct=True),
                total=Count('board_post', distinct=True) + Count('reply', distinct=True) + Count('rereply',
                                                                                                 distinct=True)
            )

        # 정렬하기
        if get_data:
            try:
                # 정렬할 때 기본으로 views를 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
                ordering = "-" + get_data['ordering']
                qs = qs.order_by(ordering, 'nickname')
            except KeyError as e:
                qs = qs.order_by('nickname')
        else:
            qs = qs.order_by('nickname')

        serializer = self.get_serializer(qs, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# 유저 별 획득 내역 확인
class PointGetView(generics.ListCreateAPIView):
    queryset = PointLog.objects.all()
    serializer_class = MyPageSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = point_raw_query(request=request, start=offset, limit=18, kind='G')

        serializer = MyPageSerializer(qs, many=True)

        # count 하기
        count_qs = PointLog.objects.filter(userid=request.user, param='G')
        count = count_qs.count()

        return Response(
            OrderedDict([('count', count), ('results', serializer.data), ('total', request.user.points)]),
            status=status.HTTP_200_OK
        )


# [쿼리 최적화 완료]
# 유저 별 사용 내역 확인
class PointUseView(generics.ListCreateAPIView):
    queryset = PointLog.objects.all()
    serializer_class = MyPageSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = point_raw_query(request=request, start=offset, limit=18, kind='U')
        serializer = MyPageSerializer(qs, many=True)

        # count
        count_qs = PointLog.objects.filter(userid=request.user, param='U')
        count = count_qs.count()

        return Response(
            OrderedDict([('count', count), ('results', serializer.data), ('total', request.user.points)]),
            status=status.HTTP_200_OK
        )


# [쿼리 최적화 완료]
# 유저 별 회수 내역 확인
class PointLoseView(generics.ListCreateAPIView):
    queryset = PointLog.objects.all()
    serializer_class = MyPageSerializer
    permission_classes = (IsAuthenticated, IsPureUser)

    def get(self, request):
        # 서브쿼리 가져오기
        get_data = request.query_params
        # 페이지 네이션
        offset = 0
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page - 1) * limit

        qs = point_raw_query(request=request, start=offset, limit=18, kind='D')
        serializer = MyPageSerializer(qs, many=True)

        # count 하기
        count_qs = PointLog.objects.filter(userid=request.user, param='D')
        count = count_qs.count()

        return Response(
            OrderedDict([('count', count), ('results', serializer.data), ('total', request.user.points)]),
            status=status.HTTP_200_OK
        )
