from django.urls import path

from image_manage.views.imagemanage_views import UploadImageView

urlpatterns = [
    # 사용자 정보 부분 알기
    path('post', UploadImageView.as_view(), name='image_post'),
]