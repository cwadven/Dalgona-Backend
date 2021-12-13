from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from battle.models import VoteBoardReplyRecommend, VoteBoardReply, VoteBoardRereplyRecommend

from battle.serializers.voteboardrecommend_serializers import (
    VoteBoardReplyRecommendSerializer, VoteBoardRereplyRecommendSerializer
)

from common.permissions import IsPureUser, IsOwnerOrSuperUserOrReadOnly


# [최적화 완료]
# 댓글 추천 및 취소
class VoteBoardReplyrecommendCreateDeleteView(generics.CreateAPIView):
    queryset = VoteBoardReplyRecommend.objects.all()
    serializer_class = VoteBoardReplyRecommendSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            if get_object_or_404(VoteBoardReply, id=serializer.validated_data["voteboardreply_id"].id).author:

                instance = serializer.validated_data['voteboardreply_id']
                qs = instance.voteboardreplyrecommend_set.filter(author=self.request.user)

                if qs.exists():
                    qs.delete()
                    return Response({"result": "recommend deleted"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    serializer.save(voteboardreply_id=instance, author=self.request.user)
                    return Response({"result": "recommend created"}, status=status.HTTP_201_CREATED)
            else:
                return Response(data={"detail": "you can't recommend at deleted reply"},
                                status=status.HTTP_400_BAD_REQUEST)


# [최적화 완료]
# 대댓글 추천 및 취소
class VoteBoardRereplyrecommendCreateDeleteView(generics.CreateAPIView):
    queryset = VoteBoardRereplyRecommend.objects.all()
    serializer_class = VoteBoardRereplyRecommendSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            instance = serializer.validated_data['voteboardrereply_id']
            qs = instance.voteboardrereplyrecommend_set.filter(author=self.request.user)

            if qs.exists():
                qs.delete()
                return Response({"result": "recommend deleted"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            serializer.save(voteboardrereply_id=instance, author=self.request.user)
            return Response({"result": "recommend created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
