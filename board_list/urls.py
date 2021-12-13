from django.urls import path, include

from rest_framework.routers import SimpleRouter


from board_list.views.boardlist_views import CategoryViewset, BoardListViewset, BoardListView

# API root view 안보이는 것 SimpleRouter 변환
router = SimpleRouter(trailing_slash=False)
router.register('category', CategoryViewset, 'category')

urlpatterns = [
    path('boardlist', BoardListViewset.as_view({'get': 'list', 'post': 'create'}), name='boardlist'),
    # division 따라 나뉘는 게시판 정보 가져옴
    path('boardlist/division/<int:division>', BoardListView.as_view(), name='boardlists'),
    path('boardlist/<str:board_url>', BoardListViewset.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
    ), name='boardlist_id'),
    path('', include(router.urls)),   
]
