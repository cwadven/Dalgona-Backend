from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status, generics

from board.models import Recommend, Scrap, Replyrecommend, Reply, Rereplyrecommend
from board.serializers.boardrecommend_serializers import (
    RecommendSerializer, ReplyrecommendSerializer,
    RereplyrecommendSerializer, ScrapSerializer
)

from rest_framework.permissions import IsAuthenticated
from common.permissions import IsPureUser, IsOwnerOrSuperUserOrReadOnly


# [쿼리 최적화 완료]
class RecommendViewset(generics.ListCreateAPIView):
    queryset = Recommend.objects.all() # id 만큼 가져오기
    serializer_class = RecommendSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 나의 추천 보기
    def get(self, request):
        qs = self.get_queryset().filter(author=request.user)
        serializer = self.get_serializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 추천 추가 및 삭제
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            recommended = self.get_queryset().filter(
                author=self.request.user,
                board_post_id=serializer.validated_data["board_post_id"]
            )
            if recommended.exists():
                recommended.delete()
                return Response(data={"detail":"recommend deleted"} , status=status.HTTP_202_ACCEPTED)
            else:
                serializer.save(author=self.request.user)
                return Response(data={"detail":"recommend created"} , status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
class ReplyrecommendViewset(generics.CreateAPIView):
    queryset = Replyrecommend.objects.all() # id 만큼 가져오기
    serializer_class = ReplyrecommendSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 추천 추가 및 삭제
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            if get_object_or_404(Reply, id=serializer.validated_data["reply_id"].id).author:
                recommended = self.get_queryset().filter(
                    author=self.request.user,
                    reply_id=serializer.validated_data["reply_id"]
                )
                if recommended.exists():
                    recommended.delete()
                    return Response(data={"detail": "reply recommend deleted"}, status=status.HTTP_202_ACCEPTED)
                else:
                    serializer.save(author=self.request.user)
                    return Response(data={"detail": "reply recommend created"}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    data={"detail": "you can't recommend at deleted reply"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
# 대댓글 추천 및 취소
class RereplyrecommendViewset(generics.CreateAPIView):
    queryset = Rereplyrecommend.objects.all() # id 만큼 가져오기
    serializer_class = RereplyrecommendSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            recommended = self.get_queryset().filter(
                author=self.request.user,
                rereply_id=serializer.validated_data["rereply_id"]
            )
            if recommended.exists():
                recommended.delete()
                return Response(data={"detail": "rereply recommend deleted"}, status=status.HTTP_202_ACCEPTED)
            else:
                serializer.save(author=self.request.user)
                return Response(data={"detail": "rereply recommend created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
class ScrapViewset(generics.ListCreateAPIView):
    queryset = Scrap.objects.all() # id 만큼 가져오기
    serializer_class = ScrapSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 나의 스크랩 보기
    def get(self, request):
        qs = self.get_queryset().filter(author=request.user)
        serializer = self.get_serializer(qs, context={"request": request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 스크랩 추가 및 삭제
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            scraped = self.get_queryset().filter(
                author=self.request.user,
                board_post_id=serializer.validated_data["board_post_id"]
            )
            if scraped.exists():
                scraped.delete()
                return Response(data={"detail": "scrap deleted"}, status=status.HTTP_202_ACCEPTED)
            else:
                serializer.save(author=self.request.user)
                return Response(data={"detail": "scrap created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
