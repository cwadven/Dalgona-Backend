import datetime

from battle.serializers.voteboardvote_serializers import VoteSerializer

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsPureUser


# post 투표하기 -> post 경우 body voteitem_id 보내면 됨
# [최적화 완료]
class VoteCreateDeleteView(APIView):
    permission_classes = (IsAuthenticated, IsPureUser)

    # 투표하기
    def post(self, request, format=None):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.validated_data['voteitem_id']

            # 마감 일자
            deadline = True if instance.voteboard_id.end_datetime < datetime.datetime.now() else False

            # 해당 투표가 마감되었는지 확인
            if deadline:
                return Response({"result": "마감된 투표입니다."}, status=status.HTTP_400_BAD_REQUEST)

            qs = instance.voteboard_id.vote_set.filter(voter=self.request.user)

            # 다른 투표 아이템에 투표가 되어있는지 확인
            if qs.exists():
                # 이미 투표를 했으면 더 이상 투표 진행 불가능
                return Response({"result": "이미 참여한 투표입니다."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(voteboard_id=instance.voteboard_id, voter=self.request.user)
            return Response({"result": "투표가 되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
