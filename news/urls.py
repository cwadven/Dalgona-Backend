from django.urls import path

from news.views.news_views import NewsDataViewset, PopularKeywordAPIView

urlpatterns = [
    # 사용자 정보 부분 알기
    path('list', NewsDataViewset.as_view(), name='news'),
    path('popular-keyword', PopularKeywordAPIView.as_view(), name='popular_keyword'),
]