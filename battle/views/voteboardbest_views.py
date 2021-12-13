import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from battle.models import VoteBoard
from battle.serializers.voteboardbest_serializers import BestVoteBoardSerializer


# [최적화 완료]
# get -> 실시간 이슈 배틀(30분)
class BestVoteView(generics.ListAPIView):
    queryset = VoteBoard.objects.prefetch_related('voteitem')
    serializer_class = BestVoteBoardSerializer
    permission_classes = (AllowAny, )

    def get(self, request):
        # 시간에 따른 투표 수에 따라서 정렬하기 (현재는 30분)
        time = timezone.datetime.now() - datetime.timedelta(hours=3)

        # 위에서부터 pk 잡힘
        qs = VoteBoard.objects.raw(f"""
        SELECT
        battle_voteboard.id,
        COUNT(*) AS vote_count
        FROM battle_vote
        INNER JOIN battle_voteitem
        ON battle_vote.voteitem_id_id = battle_voteitem.id
        INNER JOIN battle_voteboard
        ON battle_voteboard.id = battle_vote.voteboard_id_id
        WHERE battle_vote.created_at >= %(time)s
        GROUP BY battle_vote.voteboard_id_id
        ORDER BY vote_count DESC
        LIMIT 5;
        """, {'time': time})

        serializer = BestVoteBoardSerializer(qs, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)