import datetime
from django.utils import timezone

from board_list.models import Board_list


def board_list_all_raw_query(request, start, limit=18, searchType="", searchWord="", board_url=False, ordering=False):
    # SQL INJECTION 방지 append
    param_list = []

    # 검색 기능(필터링)
    title_search = False
    body_search = False
    _search = False
    _double_search = False

    # 게시판 url로 필터링하기
    if board_url:
        param_list.append(board_url)

    # 검색하기
    if searchType and searchWord:
        if searchType == 'title':
            title_search = True
            _search = True
            param_list.append('%%' + searchWord + '%%')
        elif searchType == 'body':
            body_search = True
            _search = True
            param_list.append('%%' + searchWord + '%%')
        elif searchType == 'title-body':
            _search = True
            _double_search = True
            param_list.append('%%' + searchWord + '%%')

    # SQL INJECTION 방지 append
    param_list.append(limit)
    param_list.append(start)

    # 검색 할 때, 프로시저 따로 만들어서 각 단어를 순회하도록 해야함
    # 예 : 제목이 '안녕하세요 저는 이창우 입니다' 일 경우 안녕하세요 / 저는 / 이창우 / 입니다 -> 따로 따로 앞에서 부터만 검색단어 순회
    qs = Board_list.objects.raw(f'''SELECT board_board_post.id,
        board_board_post.created_at,
        board_board_post.board_url_id,
        board_board_post.title,
        board_board_post.body,
        board_board_post.views,
        (select COUNT(board_recommend.id) FROM board_recommend WHERE board_board_post.id = board_recommend.board_post_id_id) AS recommend_count,
        (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(board_rereply.id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count,
        board_list_board_list.id,
        board_list_board_list.board_name,
        board_list_board_list.board_url
        FROM board_board_post
        INNER JOIN board_list_board_list
        ON (board_board_post.board_url_id = board_list_board_list.id)
        WHERE {"board_list_board_list.board_url = %s AND" if board_url else ''} board_list_board_list.read_priority <= {(request.user.level if request.user.is_authenticated else -1)} {'AND' if _search else ''} {"board_board_post.title LIKE %s" if title_search else ""} {"board_board_post.body LIKE %s" if body_search else ""} {"CONCAT(board_board_post.title, board_board_post.body) LIKE %s" if _double_search else ""}
        ORDER BY board_board_post.created_at DESC
        LIMIT %s
        OFFSET %s'''
                                , param_list)

    return qs


# 전체 게시글에 있는 게시판 전부 다 보여줌
# 권한에 따른 게시판의 게시글 안보여 주도록 못함 너무 시간 걸림
# 검색, 정렬 못함
def show_board_all_list_raw_query(start, limit=18):
    qs = Board_list.objects.raw(f'''
    SELECT board_board_post.id,
        board_board_post.created_at,
        board_board_post.title,
        board_board_post.body,
        board_board_post.views,
        (select board_name FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS board_name,
        (select board_url FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS board_url,
        (select division FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS division,
        (select COUNT(id) FROM board_recommend WHERE board_board_post.id = board_recommend.board_post_id_id) AS recommend_count,
        (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count
    FROM board_board_post
    order by board_board_post.created_at DESC
    LIMIT %s
    OFFSET %s''', (limit, start))
    return qs


def best_board_raw_query(minutes, division, limit=6, options="", recommend_count=1):
    time = timezone.datetime.now() - datetime.timedelta(minutes=minutes)
    qs = Board_list.objects.raw(f'''
    SELECT 
        board_board_post.id,
        board_board_post.title,
        board_board_post.body,
        board_board_post.views,
        board_board_post.created_at,
        (select COUNT(board_recommend.id) FROM board_recommend WHERE board_board_post.id = board_recommend.board_post_id_id) AS recommend_count,
        (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(board_rereply.id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count,
        COUNT(board_post_id_id) AS check_true,
        board_list_board_list.board_name,
        board_list_board_list.board_url,
        board_list_board_list.division
    FROM
        board_recommend
    INNER JOIN board_board_post
    ON (board_board_post.id = board_post_id_id)
    INNER JOIN board_list_board_list
    ON (board_board_post.board_url_id = board_list_board_list.id)
    WHERE
        board_recommend.created_at >= '{time}' AND {options} board_list_board_list.division = {division}
    GROUP BY board_post_id_id
    HAVING check_true >= {recommend_count}
    ORDER BY check_true DESC
    LIMIT {limit};'''
                                )
    return qs


def popular_board_raw_query(minutes, board_url, limit=5, recommend_count=5):
    time = timezone.datetime.now() - datetime.timedelta(minutes=minutes)
    qs = Board_list.objects.raw(f'''
    SELECT 
        board_board_post.id,
        board_board_post.title,
        board_board_post.body,
        board_board_post.views,
        board_board_post.created_at,
        (select COUNT(board_recommend.id) FROM board_recommend WHERE board_board_post.id = board_recommend.board_post_id_id) AS recommend_count,
        (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(board_rereply.id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count,
        COUNT(board_post_id_id) AS check_true,
        board_list_board_list.board_name,
        board_list_board_list.board_url,
        board_list_board_list.division
    FROM
        board_recommend
    INNER JOIN board_board_post
    ON (board_board_post.id = board_post_id_id)
    INNER JOIN board_list_board_list
    ON (board_board_post.board_url_id = board_list_board_list.id)
    WHERE
        board_recommend.created_at >= '{time}' AND NOT board_list_board_list.division = 0 AND board_list_board_list.board_url = %s
    GROUP BY board_post_id_id
    HAVING check_true >= {recommend_count}
    ORDER BY check_true DESC
    LIMIT {limit};'''
                                , (board_url,))
    return qs