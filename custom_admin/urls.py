from django.urls import path, include

from custom_admin.views.cmsaccount_views import AccountListViewset, AccountViewset
from custom_admin.views.cmsactivity_views import AccountActivityViewset
from custom_admin.views.cmsblack_views import BlackListViewset, BlackUserViewset
from custom_admin.views.cmsboard_views import BoardListDetailViewset, BoardDetailViewset, AdminBoardViewset
from custom_admin.views.cmsreply_views import AdminReplyViewset

urlpatterns = [
    # 게시판 상세 관리 (사용자 권한 설정 가능)
    path('boardlist/detail', BoardListDetailViewset.as_view(), name='boardlist_detail'),
    path('boardlist/detail/<str:board_url>', BoardDetailViewset.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
    ), name='board_detail'),
    
    # 관리자용 댓글 정보들 보기 -> 익명 안보이게
    path('board/<int:board_post_id>/reply', AdminReplyViewset.as_view({'get': 'list'}), name='admin_reply_list'),

    # 관리자용 게이슬 정보들 보기 -> 익명 안보이게
    # 모든 게시글
    path('board', AdminBoardViewset.as_view({'get': 'all_boards'}), name='admin_boards'),
    # 특정 게시판의 게시글 (게시글 작성 및 리스트 조회)
    path('board/<str:board_url>', AdminBoardViewset.as_view({'get': 'list'}), name='admin_boards'),
    # 특정 게시판의 게시글 주요정보
    path('board/<str:board_url>/<int:pk>', AdminBoardViewset.as_view({'get': 'retrieve'}), name='admin_board_detail'),

    # 게시글/게시판 기능은 기존의 API를 그대로 사용
    path('', include('board.urls')),
    path('', include('board_list.urls')),

    # 사용자 관리
    path('accountlist', AccountListViewset.as_view(), name='admin_account_list'),
    path('account/<str:username>', AccountViewset.as_view(), name='admin_account'),
    path('account/<str:username>/<str:event>/activity', AccountActivityViewset.as_view(), name='admin_user_activity'),

    # 사용자 제제
    path('blacklist', BlackListViewset.as_view(), name='blacklist'),
    path('blacklist/<int:pk>', BlackUserViewset.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='blackuser'),
    # 추후 <int:userid>와 <int:userid>/<int:pk> 형태의 url view 작성해야함

    
]