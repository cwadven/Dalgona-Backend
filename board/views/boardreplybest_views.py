from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from board.models import Reply
from board.serializers.boardreplybest_serializers import BestReplySerializer

from rest_framework.permissions import AllowAny

from django.db.models import Count, Q


# [쿼리 최적화 완료]
# [특정 속성만 가져오기]
# 인기 댓글 보기
class BestReplyViewset(generics.ListAPIView):
    queryset = Reply.objects.select_related('author').annotate(
        recommend_count=Count('replyrecommend')
    ).defer('board_post_id', 'updated_at').all()
    serializer_class = BestReplySerializer
    permission_classes = (AllowAny, )

    # 1개 이상인 댓글 추천을 가져온다! (총 10개)
    def get(self, request, board_post_id):

        # 해당 댓글에 추천한 것 중 내가 추천한게 1개 이상이라도 있으면 개수 아니면 0
        qs = self.get_queryset().annotate(
            recommended=Count('replyrecommend', distinct=True,
                filter=Q(
                    replyrecommend__author=(request.user if request.user.is_authenticated else None),
                )
            )
        )

        qs = qs.filter(board_post_id=board_post_id).filter(recommend_count__gte=1).order_by('-recommend_count')[:3]
        serializer = self.get_serializer(qs,context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)