from django.urls import path

from battle.views.voteboard_views import VoteBoardListView, VoteBoardDetailView
from battle.views.voteboardbest_views import BestVoteView
from battle.views.voteboarditem_views import VoteItemCreateView, VoteItemDetailView
from battle.views.voteboardrecommend_views import (
    VoteBoardReplyrecommendCreateDeleteView, VoteBoardRereplyrecommendCreateDeleteView
)
from battle.views.voteboardreply_views import (
    VoteReplyListView, VoteReplyCreateView, VoteReplyDetailView,
    VoteRereplyView, VoteRereplyDetailView
)
from battle.views.voteboardvote_views import VoteCreateDeleteView

urlpatterns = [
    # get - 실시간 이슈 배틀 가져오기(5개, 10분)
    path('vote/best', BestVoteView.as_view(), name='votebest'),

    # post -> 투표 아이템 생성(관리자만 가능)
    path('vote/item', VoteItemCreateView.as_view(), name='votecreate'),
    # get, put, delete -> 투표 아이템 수정, 삭제(관리자만 가능)
    path('vote/item/<int:pk>', VoteItemDetailView.as_view(), name='itemdetail'),

    # get - 해당 투표 게시글 댓글 조회
    path('vote/board/<int:voteboard_id>/reply', VoteReplyListView.as_view(), name='votereply_list'),

    # get, post -> 투표 게시판 생성, 관리자만 post 가능
    path('vote/board', VoteBoardListView.as_view(), name='voteboard'),
    # get, put, delete -> 투표 게시판 수정 삭제(관리자만 put, delete 가능)
    path('vote/board/<int:pk>', VoteBoardDetailView.as_view(), name='votedetail'),

    # post, delete -> 투표하기, 취소하기
    path('vote', VoteCreateDeleteView.as_view(), name='vote'),

    # post - 댓글 작성
    path('vote/board/reply', VoteReplyCreateView.as_view(), name='votereply_create'),
    # put, delete - 댓글 수정, 삭제
    path('vote/board/reply/<int:pk>', VoteReplyDetailView.as_view(), name='replydetail'),

    # get, post - 대댓글 작성 및 조회
    path('vote/board/rereply', VoteRereplyView.as_view(), name='voterereply'),
    # put, delete - 대댓글 수정, 삭제
    path('vote/board/rereply/<int:pk>', VoteRereplyDetailView.as_view(), name='rereplydetail'),

    # post, delete - 댓글 추천 및 취소
    path('vote/board/reply/recommend', VoteBoardReplyrecommendCreateDeleteView.as_view(), name='replyrecommend'),
    # post, delete - 대댓글 추천 및 취소
    path('vote/board/rereply/recommend', VoteBoardRereplyrecommendCreateDeleteView.as_view(), name='rereplyrecommend'),
    
]