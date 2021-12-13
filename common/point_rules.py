from custom_admin.models import PointLog
from board.models import Board_post

import datetime
from django.db.models import Q


# 별 지급 함수
def point_check(user, kind, information, points, kindid):
    # 게시글 작성 포인트
    board_point = user.pointlog_set.filter(kind='게시글 작성', created_at__gt=datetime.datetime.now().date()).count() * 2
    # 게시글 or 투표 댓글, 대댓글 작성 포인트
    reply_point = user.pointlog_set.filter(
        Q(kind='게시글 댓글 작성') | Q(kind='게시글 대댓글 작성') | Q(kind='투표 댓글 작성') | Q(kind='투표 대댓글 작성'),
        created_at__gt=datetime.datetime.now().date()
    ).count()

    total = board_point + reply_point

    # 하루에 얻은 포인트가 50미만일때만 지급
    if total + points <= 50:
        # 게시글. 댓글 작성시 포인트 지급
        PointLog.objects.create(
            userid=user,
            kind=kind,
            information=information,
            points=points,
            param='G',
            kindid=kindid
        )


# 인기게시글 달성 시, 조건에 따른 포인트 추가
def popular_board_check(queryset):
    # 어떤 인기 게시글이 있었는지를 queryset 매개변수로 가져와서 집합 자료형을 이용하여 변수에 저장
    whole_board_qs = set(queryset)

    # 인기 게시글로 받았던 적이 1번이라도 있는 경우의 id
    qs = PointLog.objects.filter(
        kind="특정 게시판 인기게시글",
        kindid__in=whole_board_qs
    ).values_list('kindid', flat=True)

    # whole_board_qs - 있는 녀석들 (차집합)
    # 없는 것들 id
    need_to_create_id = whole_board_qs - set(qs)

    # 만약 인기 게시글로 받았던 적이 없는 id가 존재할 경우
    if len(need_to_create_id):
        # 그 id를 가진 게시글 정보를 가져온다
        b_qs = Board_post.objects.select_related('author').filter(id__in=need_to_create_id)

        # 인기 게시글로 Point 준다
        for b in b_qs:
            PointLog.objects.create(
                userid=b.author,
                kind="특정 게시판 인기게시글",
                information="작성하신 게시글이 인기 게시글이 되었습니다!",
                points=3,
                param='G',
                kindid=b.id
            )
