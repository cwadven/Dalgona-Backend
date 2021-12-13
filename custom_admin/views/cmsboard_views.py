from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from board.models import Board_post
from board_list.models import Board_list

from custom_admin.serializers.cmsboard_serializers import (
    BoardListDetailSerializer, AdminBoardSerializer,
    BoardDetailSerializer
)

from common.pagination import BasicPagination
from common.permissions import IsSuperUser

import datetime


class BoardListDetailViewset(generics.ListAPIView):
    queryset = Board_list.objects.all()
    serializer_class = BoardListDetailSerializer
    permission_classes = (IsSuperUser,)

    def get(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, context={"request": request}, many=True)

        # 생성된 지 하루도 안지난 경우 is_new true 반환한다.
        for board_info in serializer.data:
            if datetime.datetime.strptime(board_info["created_at"], '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(
                    days=1) >= timezone.datetime.now():
                board_info["is_new"] = True
            else:
                board_info["is_new"] = False
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# Admin 용 익명 가져오기 위해서 설정
class AdminBoardViewset(viewsets.ModelViewSet):
    queryset = Board_post.objects.select_related('author', 'category_id').prefetch_related(
        'recommend_set',
        'scrap_set',
        'reply_set',
        'rereply_set',
    )  # id 만큼 가져오기
    serializer_class = AdminBoardSerializer
    permission_classes = (IsSuperUser,)
    # 페이지 네이션 적용
    pagination_class = BasicPagination

    # 전체 게시판에 있는 것들의 조회만 가능
    def all_boards(self, request, *args, **kwargs):
        # 권한에 맞는 글 가져오기
        if request.user.is_authenticated:
            qs = self.get_queryset().filter(board_url__read_priority__lte=request.user.level)
        else:
            qs = self.get_queryset().filter(board_url__read_priority__lte=-1)

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title, nickname / word : 제목
        # search_type=username&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                qs = qs.filter(title__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'nickname':
                qs = qs.filter(author__nickname__contains=get_data.get('searchWord'))

        # 말머리 필터링 이후 정렬하기
        if get_data.get('category_id'):
            # 말머리 필터링 쿼리 존재 시 필터링하기
            qs = qs.filter(category_id=get_data.get('category_id')) if get_data.get('category_id') is not None else qs

        if get_data.get('ordering'):
            # 정렬할 때 기본으로 views 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
            ordering = "-" + get_data.get('ordering') if get_data.get('ordering') is not None else '-created_at'
            try:
                qs = qs.order_by(ordering, '-created_at')
            except:
                pass

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 리스트로 쭉 가져오기
    def list(self, request, board_url=None):
        instance = get_object_or_404(Board_list, board_url=board_url)

        qs = self.get_queryset()

        # 서브쿼리 가져오기
        get_data = request.query_params

        # 필터링 설정 완료
        # 타입을 넣고 type, word 기준으로 word filter
        # type : title, nickname / word : 제목
        # search_type=username&search_word=단어
        if get_data.get('searchType') and get_data.get('searchWord'):
            if get_data.get('searchType') == 'title':
                qs = qs.filter(title__contains=get_data.get('searchWord'))
            elif get_data.get('searchType') == 'nickname':
                qs = qs.filter(author__nickname__contains=get_data.get('searchWord'))

        # 말머리 필터링 이후 정렬하기
        if get_data.get('category_id'):
            # 말머리 필터링 쿼리 존재 시 필터링하기
            qs = qs.filter(category_id=get_data.get('category_id')) if get_data.get('category_id') is not None else qs

        if get_data.get('ordering'):
            # 정렬할 때 기본으로 views 하면 바로 -views 처럼 내림차 순으로 기본으로 설정하기 위해서 설정
            ordering = "-" + get_data.get('ordering') if get_data.get('ordering') is not None else '-created_at'
            try:
                qs = qs.order_by(ordering, '-created_at')
            except:
                pass

        if board_url:
            # 만약에 파라미터가 있으면 필터
            qs = qs.filter(board_url__board_url=board_url)

        # 페이지 네이션 기능 추가
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
        else:
            serializer = self.get_serializer(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # detail 하나 가져오기
    def retrieve(self, request, board_url=None, pk=None):
        instance = get_object_or_404(self.get_queryset(), board_url__board_url=board_url, pk=pk)
        serializer = self.get_serializer(instance)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    @transaction.atomic
    def perform_create(self, serializer):  # 자동으로 자기 자신 author 저장 되도록
        serializer.save(author=self.request.user)

    @transaction.atomic
    def perform_update(self, serializer):  # 자동으로 자기 자신 author 저장 되도록:
        # 수정 시, author 만은 수정 하지 않도록 설정
        serializer.save()


class BoardDetailViewset(viewsets.ModelViewSet):
    queryset = Board_list.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = (IsSuperUser,)
    lookup_field = 'board_url'
