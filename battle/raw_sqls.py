from battle.models import VoteBoard

# [raw_sql 최적화 완료]
# vote board list에 사용하는 쿼리로, 검색까지
def vote_board_list_raw_query(request, start, searchType="", searchWord="", ordering=False):
    # SQL INJECTION 방지 append
    param_list = []
    param_list_for_count = []

    # 검색 기능(필터링)
    title_search = False
    content_search = False
    _search = False
    _double_search = False

    # 검색하기
    if searchType and searchWord:
        if searchType == 'title':
            title_search = True
            _search = True
            param_list.append('%%' + searchWord + '%%')
            param_list_for_count.append('%%' + searchWord + '%%')
        elif searchType == 'content':
            content_search = True
            _search = True
            param_list.append('%%' + searchWord + '%%')
            param_list_for_count.append('%%' + searchWord + '%%')
        elif searchType == 'title_content':
            _search = True
            _double_search = True
            param_list.append('%%' + searchWord + '%%')
            param_list_for_count.append('%%' + searchWord + '%%')

    # SQL INJECTION 방지 append
    param_list.append(start)

    # vote board 조건에 맞게 가져오기
    # created_at 정렬이 아닌 id로 역정렬해도 됨
    qs = VoteBoard.objects.raw(f'''SELECT battle_voteboard.id,
                battle_voteboard.title,
                battle_voteboard.content,
                battle_voteboard.board_image,
                (select COUNT(battle_vote.id) FROM battle_vote WHERE battle_voteboard.id = battle_vote.voteboard_id_id) AS vote_count,
                (select COUNT(battle_voteboardreply.id) FROM battle_voteboardreply WHERE battle_voteboard.id = battle_voteboardreply.voteboard_id_id AND battle_voteboardreply.author_id IS NOT NULL) + (select COUNT(battle_voteboardrereply.id) FROM battle_voteboardrereply WHERE battle_voteboard.id = battle_voteboardrereply.voteboard_id_id) AS reply_count,
                battle_voteboard.start_datetime,
                battle_voteboard.end_datetime,
                battle_voteboard.created_at
                FROM battle_voteboard
                {"WHERE" if _search else ''} {"battle_voteboard.title LIKE %s" if title_search else ""} {"battle_voteboard.content LIKE %s" if content_search else ""} {"CONCAT(battle_voteboard.title, battle_voteboard.content) LIKE %s" if _double_search else ""}
                ORDER BY battle_voteboard.id DESC
                LIMIT 18
                OFFSET %s'''
                               , param_list)

    # 페이지네이션에 사용
    count_qs = VoteBoard.objects.raw(f'''SELECT id, 
    COUNT(battle_voteboard.id) as count
    FROM battle_voteboard
    WHERE battle_voteboard.created_at < current_timestamp {"AND" if _search else ''} {"battle_voteboard.title LIKE %s" if title_search else ""} {"battle_voteboard.content LIKE %s" if content_search else ""} {"CONCAT(battle_voteboard.title, battle_voteboard.content) LIKE %s" if _double_search else ""}
    '''
                                     , param_list_for_count)

    return qs, count_qs