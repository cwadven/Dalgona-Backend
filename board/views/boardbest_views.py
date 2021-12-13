from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from board.models import Board_post


# [쿼리 최적화 완료 (RAW SQL)]
# [특정 속성만 가져오기]
# 루나+자유게시판 실시간 인기글 보기
from board.raw_sqls import best_board_raw_query, popular_board_raw_query
from board.serializers.board_serializers import BoardPostListRawSqlSerializer
from board.serializers.boardbest_serializers import BestBoardPostListRawSqlSerializer
from common.point_rules import popular_board_check


class BestView(generics.ListAPIView):
    queryset = Board_post.objects.all()
    serializer_class = None
    permission_classes = (AllowAny,)

    # 실시간 인기 게시글 보기
    # 시간에 따른은 추천 수에 따라서 정렬하기 (현재는 30분)
    def get(self, request):
        qs = best_board_raw_query(minutes=9999, division=0, limit=6, options="NOT")

        serializer = BestBoardPostListRawSqlSerializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# [쿼리 최적화 완료 (RAW SQL)]
# [특정 속성만 가져오기]
# 자유 게시판 실시간 인기글 가져오기
class BestFreeView(generics.ListAPIView):
    queryset = Board_post.objects.all()
    serializer = None
    permission_classes = (AllowAny,)

    # 실시간 인기 게시글 보기
    def get(self, request):
        qs = best_board_raw_query(minutes=9999, division=1, limit=6, options="")

        serializer = BestBoardPostListRawSqlSerializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# [쿼리 최적화 완료 (RAW SQL)]
# [특정 속성만 가져오기]
# 루나 게시판 실시간 인기글 가져오기
class BestLunaView(generics.ListAPIView):
    queryset = Board_post.objects.all()
    serializer = None
    permission_classes = (AllowAny,)

    # 실시간 인기 게시글 보기
    def get(self, request):
        qs = best_board_raw_query(minutes=9999, division=2, limit=6, options="")

        serializer = BestBoardPostListRawSqlSerializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 공지, 이벤트 등의 게시판 제외하고 인기글 보기
class BestBoardViewset(generics.ListAPIView):
    queryset = Board_post.objects.all()
    serializer = None
    permission_classes = (AllowAny,)

    # 인기 게시글 보기
    def get(self, request, board_url):
        qs = popular_board_raw_query(minutes=9999, board_url=board_url, limit=5, recommend_count=1)
        # RAW SQL 나온 id 이용
        queryset = [p.id for p in qs]
        popular_board_check(queryset)
        serializer = BoardPostListRawSqlSerializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)