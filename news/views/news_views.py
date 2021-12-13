from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from news.models import NewsData, PopularKeyword

from news.serializers.news_serializers import NewsSerializers, PopularKeywordSerializers

from common.pagination import BasicPagination


class NewsDataViewset(generics.ListAPIView):
    queryset = NewsData.objects.all()
    serializer_class = NewsSerializers
    pagination_class = BasicPagination

    def get(self, request):
        qs = self.get_queryset()

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title / word : 제목
        # search_type=title&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                qs = qs.filter(title__contains=get_data.get('searchWord'))

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularKeywordAPIView(generics.ListAPIView):
    queryset = PopularKeyword.objects.all()[:5]
    serializer_class = PopularKeywordSerializers
