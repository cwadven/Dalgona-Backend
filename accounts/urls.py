from django.urls import path

from rest_auth.views import UserDetailsView

from .views.auth_views import (
    ReEmailConfirmation, PhoneCertificationView, NicknameOverlap,
    EmailOverlap, UsernameOverlap
)

from .views.mypage_views import (
    PointLoseView, PointUseView, PointGetView,
    BookmarkView, BasicUpdateView, ScoreView,
    MyRereplyView, MyReplyView, MyPostView
)

urlpatterns = [
    # 사용자 정보 부분 알기
    path('profile', BasicUpdateView.as_view(), name='basic_profile'),
    # 사용자 정보 전부 알기
    path('user', UserDetailsView.as_view(), name='rest_user_details'),

    # 즐겨찾기 추가 및 삭제
    path('profile/bookmark', BookmarkView.as_view(), name='bookmark_control'),

    # 내가 쓴 글 조회
    path('profile/mypost', MyPostView.as_view(), name='my_post'),
    # 내가 쓴 댓글 조회
    path('profile/myreply', MyReplyView.as_view(), name='my_reply'),
    # 내가 쓴 대댓글 조회
    path('profile/myrereply', MyRereplyView.as_view(), name='my_rereply'),

    # 중복확인
    path('overlap/username', UsernameOverlap.as_view(), name='overlab_username'),
    path('overlap/email', EmailOverlap.as_view(), name='overlab_email'),
    path('overlap/nickname', NicknameOverlap.as_view(), name='overlab_nickname'),

    # 휴대폰 인증
    path('certification', PhoneCertificationView.as_view(), name='phone_cert'),

    # 이메일 재인증
    path('confirm', ReEmailConfirmation.as_view(), name='resend_email'),
    # # 이벤트 얼마나 많은 것을 작성 및 했는지
    path('score', ScoreView.as_view(), name='score'),

    # 마이페이지 별 내역 확인
    path('profile/mypoint/get', PointGetView.as_view(), name='my_get_point'),
    path('profile/mypoint/use', PointUseView.as_view(), name='my_use_point'),
    path('profile/mypoint/lose', PointLoseView.as_view(), name='my_lose_point'),
]
