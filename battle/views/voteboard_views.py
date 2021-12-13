from collections import OrderedDict

from rest_framework import generics, status
from rest_framework.response import Response

from battle.models import VoteBoard
from battle.raw_sqls import vote_board_list_raw_query
from battle.serializers.voteboard_serializers import (
    VoteBoardListSerializer, VoteBoardGetListSerializer,
    VoteBoardDetailSerializer, VoteBoardGetDetailSerializer
)

from common.permissions import IsSuperUserOrReadOnly


# [최적화 완료]
# get, post -> 투표 게시판 리스트로 가져오기, 작성하기
class VoteBoardListView(generics.ListCreateAPIView):
    queryset = VoteBoard.objects.all()
    serializer_class = VoteBoardListSerializer
    # IsSuperUser(permissions.py)는 get method 대해서 외부인 접근 허용
    permission_classes = (IsSuperUserOrReadOnly,)

    def list(self, request, voteboard_id=None):

        get_data = request.query_params
        # 페이지네이션
        offset = 0

        # 숫자일 경우만
        if get_data.get('page') and get_data.get('page').isdecimal():
            page = int(get_data.get('page'))
            limit = 18
            offset = (page-1) * limit

        # SQL RAW 검색 기능
        qs, count_qs = vote_board_list_raw_query(
            request=request,
            start=offset,
            searchType=get_data.get('searchType'),
            searchWord=get_data.get('searchWord')
        )

        serializer = VoteBoardGetListSerializer(qs, many=True)

        return Response(
            OrderedDict([('count', count_qs[0].count), ('results',serializer.data)]),
            status=status.HTTP_200_OK
        )


# [최적화 완료]
# get, put, delete -> 특정 투표 게시판 가져오기, 수정, 삭제
class VoteBoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VoteBoard.objects.all()
    serializer_class = VoteBoardDetailSerializer
    permission_classes = (IsSuperUserOrReadOnly,)

    def retrieve(self, request, pk):
        qs = VoteBoard.objects.raw(f'''SELECT battle_voteboard.id,
            battle_voteboard.title,
            battle_voteboard.content,
            battle_voteboard.board_image,
            battle_voteboard.start_datetime,
            battle_voteboard.end_datetime,
            battle_voteboard.created_at,
            (select count(id) from battle_vote where battle_voteboard.id = battle_vote.voteboard_id_id) AS vote_count,
            (select count(id) from battle_voteboardreply where battle_voteboard.id = battle_voteboardreply.voteboard_id_id AND battle_voteboardreply.author_id IS NOT NULL) 
                + (select count(id) from battle_voteboardrereply where battle_voteboard.id = battle_voteboardrereply.voteboard_id_id) AS reply_count,
            EXISTS(
                SELECT U0.id
                FROM battle_vote U0
                WHERE (U0.voter_id = %(voter_id)s AND U0.voteboard_id_id = %(pk)s)
            ) AS is_voted
            FROM battle_voteboard
            WHERE battle_voteboard.id = {pk}
        ''', {'voter_id': request.user.id, 'pk': pk})

        serializer = VoteBoardGetDetailSerializer(qs[0], context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)
