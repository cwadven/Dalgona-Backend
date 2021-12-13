from collections import OrderedDict

from django.db import transaction
from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from battle.models import VoteBoardReply, VoteBoardRereply

from battle.serializers.voteboardreply_serializers import (
    VoteReplyGetSerializer, VoteReplySerializer, VoteReplyDetailSerializer,
    VoteRereplySerializer, VoteRereplyDetailSerializer
)

from common.permissions import IsPureUser, IsOwnerOrSuperUserOrReadOnly
from common.pagination import BasicPagination
from custom_admin.models import PointLog
from common.point_rules import point_check


# [최적화 완료]
# 특정 게시글 댓글 조회
class VoteReplyListView(generics.ListAPIView):
    queryset = VoteBoardReply.objects.select_related('author', 'voteboard_id').annotate(recommend_count=Count('voteboardreplyrecommend')).all()
    serializer_class = VoteReplyGetSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsPureUser)
    pagination_class = BasicPagination

    def list(self, request, voteboard_id=None):
        qs = self.get_queryset().prefetch_related(
            Prefetch('voteboardrereply', queryset=VoteBoardRereply.objects.annotate(
                    recommended=Count('voteboardrereplyrecommend', distinct=True,
                        filter=Q(
                            voteboardrereplyrecommend__author=(request.user if request.user.is_authenticated else None),
                        )
                    )
                ).annotate(
                    recommend_count=Count('voteboardrereplyrecommend', distinct=True,)
                )
            ),
            Prefetch('voteboardrereply__author'),
            Prefetch('voteboardrereply__voteboardrereplyrecommend_set'),
            Prefetch('voteboardrereply__voteboardrereplyrecommend_set__author'),
        ).annotate(
            recommended=Count('voteboardreplyrecommend', distinct=True,
                filter=Q(
                    voteboardreplyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            )
        )

        # 정렬하기
        get_data = request.query_params

        if voteboard_id:
            # 만약에 url에 voteboard_id가 있으면 필터
            qs = qs.filter(voteboard_id__id=voteboard_id)

        if get_data:
            try:
                # 순서 정렬하기
                ordering = "-"+get_data['ordering']
                qs = qs.annotate(recommend_count=Count('voteboardreplyrecommend')).order_by(ordering)
            except:
                qs = qs.annotate(recommend_count=Count('voteboardreplyrecommend'))

        # 총 댓글 개수 최신화
        total_count = qs.filter(author_id__isnull=False).count() + VoteBoardRereply.objects.filter(voteboard_id=voteboard_id, author_id__isnull=False).count()
        count = qs.count()

        # 페이지 네이션
        offset = 0
        limit = 10
        
        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            offset = (page-1) * limit
        else:
            page = 1
            offset = (page-1) * limit

        qs = qs[offset:offset+limit]

        serializer = self.get_serializer(qs, context={"request": request}, many=True)

        return Response(OrderedDict([('count', count), ('total_count', total_count), ('results',serializer.data)]), status=status.HTTP_200_OK)


# [최적화 완료]
# 댓글 작성
class VoteReplyCreateView(generics.CreateAPIView):
    queryset = VoteBoardReply.objects.all()
    serializer_class = VoteReplySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsPureUser)

    @transaction.atomic
    def perform_create(self, serializer): #자동으로 자기 자신 author에 저장 되도록
        created = serializer.save(author=self.request.user)
        
        # 해당 유저가 하루에 받은 포인트가 50미만일 경우 포인트 지급, 아니라면 미지급
        point_check(user=self.request.user, kind='투표댓글작성', information="투표 댓글 작성으로 포인트가 추가 되었습니다", points=1, kindid=created.id)


# [최적화 완료]
# 댓글 수정 및 삭제
class VoteReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VoteBoardReply.objects.all()
    serializer_class = VoteReplyDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 댓글 삭제할 경우 대댓글이 있으면 살아있게 만들기
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])

        # 관리자가 삭제했는지 혹은 유저가 삭제했는지
        if self.request.user.is_superuser:            
            # 대댓글이 존재하면 사용자 이름과 내용은 삭제된 댓글이라고 표현
            if instance.voteboardrereply.all().exists():
                # 투표 댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표댓글삭제", information="관리자의 투표 댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
                
                instance.author = None
                instance.content = '삭제된 댓글 입니다!'
                instance.save()
        
                return Response(status=status.HTTP_200_OK)
            else:
                # 투표 댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표댓글삭제", information="관리자의 투표 댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
                return super(VoteReplyDetailView, self).destroy(request, *args, **kwargs)
        else:
            # 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함
            if self.request.user.points - 1 < 0:
                return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

            # 대댓글이 존재하면 사용자 이름과 내용은 삭제된 댓글이라고 표현
            if instance.voteboardrereply.all().exists():
                # 투표 댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표댓글삭제", information="투표 댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])

                instance.author = None
                instance.content = '삭제된 댓글 입니다!'
                instance.save()
        
                return Response(status=status.HTTP_200_OK)
            else:
                # 투표 댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표댓글삭제", information="투표 댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
                return super(VoteReplyDetailView, self).destroy(request, *args, **kwargs)


# [최적화 완료]
# 대댓글 작성 및 조회
class VoteRereplyView(generics.ListCreateAPIView):
    queryset = VoteBoardRereply.objects.annotate(recommend_count=Count('voteboardrereplyrecommend')).all()
    serializer_class = VoteRereplySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsPureUser)

    def create(self, request, *args, **kwargs):
        reply_id = request.POST.get('voteboardreply_id','')
        if reply_id:
            query = get_object_or_404(VoteBoardReply, id=reply_id)
            if query.author:
                return super(VoteRereplyView, self).create(request, *args, **kwargs)
            else:
                return Response(data={"detail":"you can't create rereply at deleted reply"} , status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def perform_create(self, serializer): #자동으로 자기 자신 author에 저장 되도록
        if serializer.is_valid():
            voteboard_id = serializer.validated_data["voteboardreply_id"].voteboard_id
            created = serializer.save(author=self.request.user, voteboard_id=voteboard_id)

            # 해당 유저가 하루에 받은 포인트가 50미만일 경우 포인트 지급, 아니라면 미지급
            point_check(user=self.request.user, kind='투표대댓글작성', information="투표 대댓글 작성으로 포인트가 추가 되었습니다", points=1, kindid=created.id)


# [최적화 완료]    
# 대댓글 수정 및 삭제
class VoteRereplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VoteBoardRereply.objects.all()
    serializer_class = VoteRereplyDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 댓글 삭제할 경우 대댓글이 있으면 살아있게 만들기
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])

        # 관리자가 삭제했는지 혹은 유저가 삭제했는지
        if self.request.user.is_superuser:            
            # author가 값이 없고(댓글이 삭제된 것), 답글이 1개만 있을 경우 삭제
            if not instance.voteboardreply_id.author and instance.voteboardreply_id.voteboardrereply.all().count() == 1:
                reply_instance = get_object_or_404(VoteBoardReply, id=instance.voteboardreply_id.id)
                reply_instance.delete()
                # 투표 대댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표대댓글삭제", information="관리자의 투표 대댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
                return Response(status=status.HTTP_200_OK)

            # 투표 대댓글 삭제시 포인트 차감
            PointLog.objects.create(userid=instance.author, kind="투표대댓글삭제", information="관리자의 투표 대댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
            return super(VoteRereplyDetailView, self).destroy(request, *args, **kwargs)
        else:
            # 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함
            if self.request.user.points - 1 < 0:
                return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

            # author가 값이 없고(댓글이 삭제된 것), 답글이 1개만 있을 경우 삭제
            if not instance.voteboardreply_id.author and instance.voteboardreply_id.voteboardrereply.all().count() == 1:
                reply_instance = get_object_or_404(VoteBoardReply, id=instance.voteboardreply_id.id)
                reply_instance.delete()
                # 투표 대댓글 삭제시 포인트 차감
                PointLog.objects.create(userid=instance.author, kind="투표대댓글삭제", information="투표 대댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
                return Response(status=status.HTTP_200_OK)

            # 투표 대댓글 삭제시 포인트 차감
            PointLog.objects.create(userid=instance.author, kind="투표대댓글삭제", information="투표 대댓글 삭제로 받은 포인트가 회수됩니다.", points=1, param='D', kindid=kwargs['pk'])
            return super(VoteRereplyDetailView, self).destroy(request, *args, **kwargs)
