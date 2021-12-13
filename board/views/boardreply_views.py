from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets, status

from board.models import Reply, Rereply
from board.serializers.boardreply_serializers import (
    ReplySerializer, ReplyGetSerializer, ReplyDetailSerializer,
    RereplySerializer, RereplyGetSerializer, RereplyDetailSerializer
)

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from common.permissions import IsPureUser, IsOwnerOrSuperUserOrReadOnly

# 포인트 관련
from custom_admin.models import PointLog

# pagination 추가
from common.pagination import BasicReplyPagination

# annotate 사용
from django.db.models import Count, Q, Prefetch

# 트랜잭션
from django.db import transaction

# 별 지급 및 인기게시글 조건
from common.point_rules import point_check

from collections import OrderedDict


# [쿼리 최적화 진행 중 -- 대댓글 정보 또한 해야함]
# 추후에 url 들어오면 해당 url 있는 것을 get 가져오도록 APIVIEW 필요
class ReplyViewset(viewsets.ModelViewSet):
    # 모든 객체를 prefetch_related 해야만이 전부 하나로 통일 됨...
    queryset = Reply.objects.select_related('author', 'board_post_id').annotate(
        recommend_count=Count('replyrecommend'),
    ).all() # id 만큼 가져오기
    serializer_class = ReplySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    # 페이지 네이션 적용
    pagination_class = BasicReplyPagination

    # 특정 게시글의 모든 댓글 가져오기
    def list(self, request, board_post_id=None):

        # Prefetched 이용하여 대댓글 쿼리를 직접 annotate 추가해 추천한 것 중 내가 추천한게 1개 이상이라도 있으면 개수 아니면 0
        qs = self.get_queryset().prefetch_related(
            Prefetch('rereply', queryset=Rereply.objects.annotate(
                    recommended=Count('rereplyrecommend', distinct=True,
                        filter=Q(
                            rereplyrecommend__author=(request.user if request.user.is_authenticated else None),
                        )
                    )
                ).annotate(
                    recommend_count=Count('rereplyrecommend', distinct=True,)
                )
            ),
            Prefetch('rereply__author'),
            Prefetch('rereply__rereplyrecommend_set'),
            Prefetch('rereply__rereplyrecommend_set__author'),
        ).annotate(
            recommended=Count('replyrecommend', distinct=True,
                filter=Q(
                    replyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            ),
        )

        # 정렬하기
        get_data = request.query_params

        if board_post_id:
            # 만약에 url board_post_id가 있으면 필터
            qs = qs.filter(board_post_id__id=board_post_id)

        if get_data:
            try:
                # 순서 정렬하기
                ordering = "-"+get_data['ordering']
                qs = qs.order_by(ordering)
            except:
                pass

        # 총 댓글 개수 최신화
        total_count = qs.filter(author_id__isnull=False).count() + Rereply.objects.filter(board_post_id=board_post_id, author_id__isnull=False).count()
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

        serializer = ReplyGetSerializer(qs, context={"request": request}, many=True)

        return Response(
            OrderedDict([('count', count), ('total_count', total_count), ('results', serializer.data)]),
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def perform_create(self, serializer): # 자동으로 자기 자신 author 저장 되도록
        created = serializer.save(author=self.request.user)

        # 해당 유저가 하루에 받은 포인트가 50미만일 경우 포인트 지급, 아니라면 미지급
        point_check(
            user=self.request.user,
            kind='게시글댓글작성',
            information="게시글 댓글 작성으로 포인트가 추가 되었습니다",
            points=1,
            kindid=created.id
        )

    # 댓글 삭제할 경우 대댓글이 있으면 살아있게 만들기
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])

        # 관리자가 삭제했는지 혹은 유저가 삭제했는지
        if self.request.user.is_superuser:
            # 댓글 삭제시 포인트 차감
            # 대댓글이 존재하면 사용자 이름과 내용은 삭제된 댓글이라고 표현
            if instance.rereply.all().exists():
                # 게시글 댓글 삭제시 포인트 차감
                PointLog.objects.create(
                    userid=instance.author,
                    kind="게시글댓글삭제",
                    information="관리자의 댓글 삭제로 받은 포인트가 회수됩니다.",
                    points=1,
                    param='D',
                    kindid=kwargs['pk']
                )

                instance.author = None
                instance.body = '삭제된 댓글 입니다!'
                instance.save()

                return Response(status=status.HTTP_200_OK)
            else:
                PointLog.objects.create(
                    userid=instance.author,
                    kind="게시글댓글삭제",
                    information="관리자의 댓글 삭제로 받은 포인트가 회수됩니다.",
                    points=1,
                    param='D',
                    kindid=kwargs['pk']
                )
                return super(ReplyViewset, self).destroy(request, *args, **kwargs)
        else:
            # 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함
            if self.request.user.points - 1 < 0:
                return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

            # 대댓글이 존재하면 사용자 이름과 내용은 삭제된 댓글이라고 표현
            if instance.rereply.all().exists():
                # 게시글 댓글 삭제시 포인트 차감
                PointLog.objects.create(
                    userid=instance.author,
                    kind="게시글댓글삭제",
                    information="게시글 댓글 삭제로 받은 포인트가 회수됩니다.",
                    points=1,
                    param='D',
                    kindid=kwargs['pk']
                )

                instance.author = None
                instance.body = '삭제된 댓글 입니다!'
                instance.save()

                return Response(status=status.HTTP_200_OK)
            else:
                # 게시글 댓글 삭제시 포인트 차감
                PointLog.objects.create(
                    userid=instance.author,
                    kind="게시글댓글삭제",
                    information="게시글 댓글 삭제로 받은 포인트가 회수됩니다.",
                    points=1,
                    param='D',
                    kindid=kwargs['pk']
                )
                return super(ReplyViewset, self).destroy(request, *args, **kwargs)

    # 댓글 수정
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ReplyDetailSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 수정 후 쿼리 조회를 하는 최적화
        qs = self.get_queryset().annotate(
            recommended=Count('replyrecommend', distinct=True,
                filter=Q(
                    replyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            )
        )

        instance = get_object_or_404(qs, pk=instance.id)

        serializer = ReplyGetSerializer(instance, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class RereplyViewset(viewsets.ModelViewSet):
    queryset = Rereply.objects.annotate(recommend_count=Count('rereplyrecommend')).all() # id 만큼 가져오기
    serializer_class = RereplySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrSuperUserOrReadOnly, IsPureUser)

    def create(self, request, *args, **kwargs):
        reply_id = request.POST.get('reply_id','')
        if reply_id:
            query = get_object_or_404(Reply, id=reply_id)
            if query.author:
                return super(RereplyViewset, self).create(request, *args, **kwargs)
            else:
                return Response(
                    data={"detail": "you can't create rereply at deleted reply"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        

    @transaction.atomic
    def perform_create(self, serializer): # 자동으로 자기 자신 author 저장 되도록
        if serializer.is_valid():
            # 잘 생성 될 경우 board_post_id는 reply_id의 board_post_id를 통해서 넣는다 --> 게시글의 모든 댓글 + 대댓글을 알기 위해서
            board_post_id = serializer.validated_data["reply_id"].board_post_id
            created = serializer.save(author=self.request.user, board_post_id=board_post_id)

            if created:
                # 해당 유저가 하루에 받은 포인트가 50미만일 경우 포인트 지급, 아니라면 미지급
                point_check(
                    user=self.request.user,
                    kind='게시글대댓글작성',
                    information="게시글 대댓글 작성으로 포인트가 추가 되었습니다",
                    points=1,
                    kindid=created.id
                )

    # 댓글 삭제할 경우 대댓글이 있으면 살아있게 만들기
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])

        # 관리자가 삭제했는지 혹은 유저가 삭제했는지
        if self.request.user.is_superuser:
            # author 값이 없고(댓글이 삭제된 것), 답글이 1개만 있을 경우 삭제
            if not instance.reply_id.author and instance.reply_id.rereply.all().count() == 1:
                reply_instance = get_object_or_404(Reply, id=instance.reply_id.id)
                reply_instance.delete()

                # 대댓글 삭제시 포인트 차감
                PointLog.objects.create(
                    userid=instance.author, 
                    kind="게시글대댓글삭제", 
                    information="관리자의 게시글 대댓글 삭제로 받은 포인트가 회수됩니다.", 
                    points=1, 
                    param='D', 
                    kindid=kwargs['pk']
                )
                return Response(status=status.HTTP_200_OK)

            # 댓글 삭제시 포인트 차감
            PointLog.objects.create(
                userid=instance.author,
                kind="게시글대댓글삭제",
                information="관리자의 게시글 대댓글 삭제로 받은 포인트가 회수됩니다.",
                points=1,
                param='D',
                kindid=kwargs['pk']
            )
            return super(RereplyViewset, self).destroy(request, *args, **kwargs)
        else:
            # 삭제할 때 포인트가 0보다 작을 경우 삭제 못하게 함
            if self.request.user.points - 1 < 0:
                return Response({"result": "not enough point"}, status=status.HTTP_400_BAD_REQUEST)

            # author 값이 없고(댓글이 삭제된 것), 답글이 1개만 있을 경우 삭제
            if not instance.reply_id.author and instance.reply_id.rereply.all().count() == 1:
                reply_instance = get_object_or_404(Reply, id=instance.reply_id.id)
                reply_instance.delete()

                # 대댓글 삭제시 포인트 차감
                PointLog.objects.create(
                    userid=instance.author,
                    kind="게시글대댓글삭제",
                    information="게시글 대댓글 삭제로 받은 포인트가 회수됩니다.",
                    points=1,
                    param='D',
                    kindid=kwargs['pk']
                )
                return Response(status=status.HTTP_200_OK)

            # 대댓글 삭제시 포인트 차감
            PointLog.objects.create(
                userid=instance.author,
                kind="게시글대댓글삭제",
                information="게시글 대댓글 삭제로 받은 포인트가 회수됩니다.",
                points=1,
                param='D',
                kindid=kwargs['pk']
            )
            return super(RereplyViewset, self).destroy(request, *args, **kwargs)

    def retrieve(self, request, pk):
        qs = self.get_queryset().annotate(
            recommended=Count('rereplyrecommend', distinct=True,
                filter=Q(
                    rereplyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            )
        )

        instance = get_object_or_404(qs, pk=pk)

        serializer = RereplyGetSerializer(instance, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 대댓글 수정
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = RereplyDetailSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 수정 후 쿼리 조회를 하는 최적화
        qs = self.get_queryset().annotate(
            recommended=Count('rereplyrecommend', distinct=True,
                filter=Q(
                    rereplyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            )
        )

        instance = get_object_or_404(qs, pk=instance.id)

        serializer = RereplyGetSerializer(instance, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)
