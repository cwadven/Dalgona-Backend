from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response

from custom_admin.serializers.cmsactivity_serializers import (
    AccountActivityBoardSerializer, AccountActivityReplySerializer,
    AccountActivityRereplySerializer, AccountActivityScrapSerializer
)

from accounts.models import Profile

from common.pagination import AccountPageNumberPagination
from common.permissions import IsSuperUser


# 사용자 활동 기록 보기
class AccountActivityViewset(generics.ListAPIView):
    queryset = Profile.objects.all()
    # serializer_class = AccountProfileSerializer
    pagination_class = AccountPageNumberPagination
    permission_classes = (IsSuperUser,)

    # 검색 기능 추가해야하나?
    def get(self, request, username, event):
        instance = get_object_or_404(self.get_queryset(), username=username)
        _filter = request.query_params

        if event == 'board':
            qs = instance.board_post_set.all()

            if _filter.get('searchType') and _filter.get('searchWord'):
                if _filter.get('searchType') == 'board':
                    qs = qs.filter(board_url__board_name__contains=_filter.get('searchWord'))
                elif _filter.get('searchType') == 'title':
                    qs = qs.filter(title__contains=_filter.get('searchWord'))

            qs = self.filter_queryset(qs)
            page = self.paginate_queryset(qs)

            if page is not None:
                serializer = self.get_paginated_response(
                    AccountActivityBoardSerializer(
                        page,
                        context={"request": request},
                        many=True
                    ).data
                )
            else:
                serializer = AccountActivityBoardSerializer(page, context={"request": request}, many=True)

        elif event == 'reply':
            qs = instance.reply_set.all()

            if _filter.get('searchType') and _filter.get('searchWord'):
                if _filter.get('searchType') == 'board':
                    qs = qs.filter(board_post_id__board_url__board_name__contains=_filter.get('searchWord'))
                elif _filter.get('searchType') == 'title':
                    qs = qs.filter(board_post_id__title__contains=_filter.get('searchWord'))
            qs = self.filter_queryset(qs)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_paginated_response(
                    AccountActivityReplySerializer(
                        page,
                        context={"request": request},
                        many=True
                    ).data
                )
            else:
                serializer = AccountActivityReplySerializer(page, context={"request": request}, many=True)
        elif event == 'rereply':
            qs = instance.rereply_set.all()

            if _filter.get('searchType') and _filter.get('searchWord'):
                if _filter.get('searchType') == 'board':
                    qs = qs.filter(board_post_id__board_url__board_name__contains=_filter.get('searchWord'))
                elif _filter.get('searchType') == 'title':
                    qs = qs.filter(board_post_id__title__contains=_filter.get('searchWord'))
            qs = self.filter_queryset(qs)
            page = self.paginate_queryset(qs)

            if page is not None:
                serializer = self.get_paginated_response(
                    AccountActivityRereplySerializer(
                        page,
                        context={"request": request},
                        many=True
                    ).data)
            else:
                serializer = AccountActivityRereplySerializer(page, context={"request": request}, many=True)
        elif event == 'scrap':
            qs = instance.scrap_set.all()

            if _filter.get('searchType') and _filter.get('searchWord'):
                if _filter.get('searchType') == 'board':
                    qs = qs.filter(board_post_id__board_url__board_name__contains=_filter.get('searchWord'))
                elif _filter.get('searchType') == 'title':
                    qs = qs.filter(board_post_id__title__contains=_filter.get('searchWord'))
            qs = self.filter_queryset(qs)
            page = self.paginate_queryset(qs)

            if page is not None:
                serializer = self.get_paginated_response(
                    AccountActivityScrapSerializer(
                        page,
                        context={"request": request},
                        many=True
                    ).data
                )
            else:
                serializer = AccountActivityScrapSerializer(page, context={"request": request}, many=True)
        else:
            return Response(data={"detail": "Not found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=serializer.data, status=status.HTTP_200_OK)