from django.shortcuts import get_object_or_404
from rest_framework import generics, status

from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from custom_admin.serializers.cmsaccount_serializers import (
    AccountListSerializer, AccountProfileSerializer,
    AdminAccountUpdateSerializer
)

from accounts.models import Profile

from common.pagination import AccountPageNumberPagination
from common.permissions import IsSuperUser


class AccountListViewset(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = AccountListSerializer
    pagination_class = AccountPageNumberPagination
    permission_classes = (IsSuperUser,)

    filter_backends = [OrderingFilter]
    ordering_fields = ['date_joined', 'level', 'username', 'last_login']

    def get(self, request):
        qs = self.get_queryset()
        qs = qs.order_by('username', '-level', '-last_login', 'date_joined')

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : username, nickname / word : root
        # search_type=username&search_word=단어
        _filter = request.query_params

        if _filter.get('searchType') and _filter.get('searchWord'):
            if _filter.get('searchType') == 'username':
                qs = qs.filter(username__contains=_filter.get('searchWord'))
            elif _filter.get('searchType') == 'nickname':
                qs = qs.filter(nickname__contains=_filter.get('searchWord'))

        qs = self.filter_queryset(qs)

        # 페이지네이션
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(
                self.get_serializer(page, context={"request": request}, many=True).data)
        else:
            serializer = self.get_serializer(page, context={"request": request}, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AccountViewset(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = AccountProfileSerializer
    permission_classes = (IsSuperUser,)

    def get(self, request, username):
        instance = get_object_or_404(self.get_queryset(), username=username)
        serializer = self.get_serializer(instance, context={"request": request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 수정하기
    def put(self, request, username):
        instance = self.get_queryset().get(username=username)
        # 기존의 경우
        serializer = AdminAccountUpdateSerializer(instance, data=request.data, context={"request": request}, )
        if serializer.is_valid():
            serializer.save()
            updated_serializer = self.get_serializer(instance, context={"request": request})
            return Response(data=updated_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)