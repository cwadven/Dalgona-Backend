from django.urls import path

from board.views.board_views import (
    NewBoardViewset, SearchViewset, BoardPostListAllAPIView,
    BoardViewset, BoardPostListAPIView
)
from board.views.boardbest_views import (
    BestFreeView, BestView, BestLunaView, BestBoardViewset
)
from board.views.boardrecommend_views import (
    ReplyrecommendViewset, RereplyrecommendViewset, RecommendViewset,
    ScrapViewset,
)
from board.views.boardreply_views import ReplyViewset, RereplyViewset
from board.views.boardreplybest_views import BestReplyViewset

urlpatterns = [
    # 해당 게시글 댓글 조회
    path('board/<int:board_post_id>/reply', ReplyViewset.as_view({'get': 'list'}), name='reply_list'),
    # 해당 게시글 인기 댓글 조회 (추천순)
    path('board/<int:board_post_id>/reply/best', BestReplyViewset.as_view(), name='best_reply'),

    # 댓글 작성
    path('board/reply', ReplyViewset.as_view({'post': 'create'}), name='reply_create'),
    # 댓글 추천 (내가추천한댓글보기, 추가, 삭제)
    path('board/reply/recommend', ReplyrecommendViewset.as_view(), name='reply_recommend'),
    # 댓글 삭제, 수정
    path('board/reply/<int:pk>', ReplyViewset.as_view({'delete': 'destroy', 'put': 'update'}), name='reply_detail'),

    # 대댓글 작성
    path('board/rereply', RereplyViewset.as_view({'post': 'create'}), name='rereply_create'),
    # 대댓글 추천
    path('board/rereply/recommend', RereplyrecommendViewset.as_view(), name='rereply_recommend'),
    # 대댓글 삭제, 수정
    path('board/rereply/<int:pk>', RereplyViewset.as_view({'delete': 'destroy', 'put': 'update'}), name='rereply_detail'),

    # 나의 추천 보기, 추가, 삭제
    path('board/recommend', RecommendViewset.as_view(), name='recommend'),
    # 나의 스크랩 보기, 추가, 삭제 
    path('board/scrap', ScrapViewset.as_view(), name='scrap'),

    # 모든 게시판 중 최신 게시글
    path('board/new', NewBoardViewset.as_view(), name='new'),
    # 자유 게시판 중 실시간 인기글
    path('board/hot/free', BestFreeView.as_view(), name='hotfree'),
    # 루나 게시판 중 실시간 인기글
    path('board/hot/luna', BestLunaView.as_view(), name='hotluna'),
    # 모든 게시판 중 실시간 인기글
    path('board/hot', BestView.as_view(), name='hot'),
    # 특정 게시판 중 인기글 -> 이 url 접속해야 포인트 3점 부여
    path('board/<str:board_url>/best', BestBoardViewset.as_view(), name='best'),

    # 게시판 검색 결과용 url
    path('board/search', SearchViewset.as_view(), name='search_board'),

    # 모든 게시글
    path('board', BoardPostListAllAPIView.as_view(), name='all_boards_list_all'),
    # 특정 게시판의 게시글 (게시글 작성)
    # 이게 밑에 있는 get 보다 먼저 있어야 함 안그러면 POST 메서드 작동 안함
    path('board/<str:board_url>/posts', BoardViewset.as_view({'post': 'create'}), name='all_board'),
    # 특정 게시판의 게시글 (리스트 조회)
    path('board/<str:board_url>', BoardPostListAPIView.as_view(), name='all_board_list'),
    # 특정 게시판의 게시글 조회 수정 삭제
    path('board/<str:board_url>/<int:pk>', BoardViewset.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
    ), name='board'),
]
