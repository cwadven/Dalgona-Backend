from django.db.models import Count

from rest_framework.response import Response
from rest_framework import viewsets

from board.models import Reply

from custom_admin.serializers.cmsreply_serializers import AdminReplySerializer

from common.pagination import BasicPagination
from common.permissions import IsSuperUser


# 댓글 가져오기 (익명(nickname))
class AdminReplyViewset(viewsets.ModelViewSet):
    queryset = Reply.objects.all()  # id 만큼 가져오기
    serializer_class = AdminReplySerializer
    permission_classes = (IsSuperUser,)

    # 페이지 네이션 적용
    pagination_class = BasicPagination

    # 특정 게시글의 모든 댓글 가져오기
    def list(self, request, board_post_id=None):
        qs = self.get_queryset()

        # 정렬하기
        get_data = request.query_params

        if board_post_id:
            # 만약에 url board_post_id가 있으면 필터
            qs = qs.filter(board_post_id__id=board_post_id)

        if get_data:
            try:
                # 순서 정렬하기
                ordering = "-" + get_data['ordering']
                qs = qs.annotate(recommend_count=Count('replyrecommend')).order_by(ordering)
            except:
                qs = qs.annotate(recommend_count=Count('replyrecommend'))

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data)
