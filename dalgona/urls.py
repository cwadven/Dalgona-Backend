from django.contrib import admin
from django.urls import path, include, re_path
from rest_auth.registration.views import VerifyEmailView
from django.conf.urls import url

from accounts.views.auth_views import ConfirmEmailView, EmailToUsernameView, NewPasswordResetView, RegisterView, PhoneCertificationFindView

from rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetConfirmView
)

from django.conf import settings
from django.conf.urls.static import static

# API 자동화
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Dalgona API",
        default_version='v1',
        description="달고나 1단계",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('custom-admin/', include('custom_admin.urls')),
    path('news/',include('news.urls')),
    
    path('', include('board.urls')),
    path('', include('board_list.urls')),
    
    # 배틀 앱 url
    path('battle/', include('battle.urls')),

    path('images/', include('image_manage.urls')),

    # 회원 관리 앱 기능들 (수정, 삭제, 중복확인)
    path('accounts/', include('accounts.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # 로그인
    path('rest-auth/login', LoginView.as_view(), name='rest_login'),
    path('rest-auth/logout', LogoutView.as_view(), name='rest_logout'),
    path('rest-auth/password/change', PasswordChangeView.as_view(), name='rest_password_change'),

    # 회원가입
    # path("rest-auth/registration", include('rest_auth.registration.urls')),
    path("rest-auth/registration", RegisterView.as_view(), name='rest_register'),

    # 이메일 인증하기
    path('accounts/allauth/', include('allauth.urls')),
    re_path(r'^account-confirm/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'^account-confirm/(?P<key>[-:\w]+)$', ConfirmEmailView.as_view(), name='account_confirm_email'),

    # username 찾기(email)
    path('username-find', EmailToUsernameView.as_view(), name='find_username'),
    # 비밀번호 찾기(email)
    # url에 uidb64 위치와 token 위치에 있는 것을 POST에 같이 넘기면 됨
    path('password-reset', NewPasswordResetView.as_view(), name='rest_password_reset'),    
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # 회원정보 찾기 (다날)
    path('account-find', PhoneCertificationFindView.as_view(), name='find_user_info_phone'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns