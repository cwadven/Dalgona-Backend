from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from board_list.models import Category, Board_list
from board_list.serializers.boardlist_serializers import CategorySerializer, BoardListSerializer

from common.permissions import IsSuperUserOrReadOnly


class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsSuperUserOrReadOnly,)


# 추후에 url 들어오면 해당 url 있는 것을 get 가져오도록 APIVIEW 필요
class BoardListViewset(viewsets.ModelViewSet):
    queryset = Board_list.objects.all()
    # id 만큼 가져오기
    serializer_class = BoardListSerializer
    # 관리자만 작성 가능 만들기 (지금은 이메일 인증한사람만 가능)
    permission_classes = (IsSuperUserOrReadOnly,)
    # 숫자 pk를 보지 않고 파라미터의 board_url 기준으로 pk 가져온다!! PUT, DELETE, GET
    # 유니크한 키만 사용
    lookup_field = 'board_url'


# division 따라 나뉘는 게시판 정보 가져옴
class BoardListView(generics.ListAPIView):
    queryset = Board_list.objects.all()
    serializer_class = BoardListSerializer

    def get(self, request, division):
        qs = self.get_queryset().filter(division=division).order_by('board_name')
        serializer = self.get_serializer(qs, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
