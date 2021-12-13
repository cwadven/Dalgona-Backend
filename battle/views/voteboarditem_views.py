from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from battle.models import VoteItem

from battle.serializers.voteboarditem_serializers import (
    VoteItemDetailSerializer, VoteItemGetDetailSerializer, VoteItemSerializer
)

from common.permissions import IsSuperUserOrReadOnly


# [최적화 완료]
# post -> 투표 아이템 생성
class VoteItemCreateView(generics.CreateAPIView):
    queryset = VoteItem.objects.all()
    serializer_class = VoteItemSerializer
    permission_classes = (IsSuperUserOrReadOnly,)


# [최적화 완료]
# get, put, delete -> 투표 아이템 가져오기, 수정, 삭제
class VoteItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VoteItem.objects.all()
    serializer_class = VoteItemDetailSerializer
    permission_classes = (IsSuperUserOrReadOnly,)

    def retrieve(self, request, pk):
        qs = self.get_queryset().annotate(vote_count=Count('vote', distinct=True)).annotate(
            is_voted=Count('vote', distinct=True,
                filter=Q(
                    vote__voter=(request.user if request.user.is_authenticated else None),
                )
            )
        ).annotate(vote_count=Count('vote', distinct=True,))

        instance = get_object_or_404(qs, pk=pk)

        serializer = VoteItemGetDetailSerializer(instance, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)
