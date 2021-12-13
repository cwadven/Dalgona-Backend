from board.models import Reply, Rereply
from board_list.models import Board_list
from custom_admin.models import PointLog


# [raw sql 완료]
def my_post_list_raw_query(request, start, limit=18):
    qs = Board_list.objects.raw(f"""
        SELECT board_board_post.id,
            board_board_post.title,
            board_board_post.body,
            board_board_post.created_at,
            (select board_name FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS board_name,
            (select board_url FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS board_url,
            (select division FROM board_list_board_list WHERE board_board_post.board_url_id = board_list_board_list.id) AS division,
            (select COUNT(board_reply.id) FROM board_reply WHERE board_board_post.id = board_reply.board_post_id_id AND board_reply.author_id IS NOT NULL) + (select COUNT(id) FROM board_rereply WHERE board_board_post.id = board_rereply.board_post_id_id) AS reply_count
        FROM board_board_post
        WHERE board_board_post.author_id = %s
        order by board_board_post.created_at DESC
        LIMIT %s
        OFFSET %s
        """, (request.user.id, limit, start))

    return qs


# [raw sql 완료]
def my_reply_list_raw_query(request, start, limit=18):
    qs = Reply.objects.raw(f"""
        SELECT board_reply.id ,
        board_reply.created_at ,
        board_reply.author_id ,
        board_reply.board_post_id_id ,
        board_reply.body ,
        board_reply.reply_image ,
        (select COUNT(board_replyrecommend.id) FROM board_replyrecommend WHERE board_reply.id = board_replyrecommend.reply_id_id) AS recommend_count ,
        accounts_profile.id ,
        board_board_post.id ,
        board_board_post.created_at ,
        board_board_post.author_id ,
        board_board_post.board_url_id
        FROM board_reply
        INNER JOIN  accounts_profile
        ON ( board_reply.author_id = accounts_profile.id )
        INNER JOIN  board_board_post 
        ON ( board_reply.board_post_id_id = board_board_post.id )
        WHERE board_reply.author_id = %s 
        ORDER BY board_reply.id DESC
        LIMIT %s
        OFFSET %s
        """, (request.user.id, limit, start))

    return qs


# [raw sql 완료]
def my_rereply_list_raw_query(request, start, limit=18):
    qs = Rereply.objects.raw(f"""
        SELECT board_rereply.id ,
        board_rereply.created_at ,
        board_rereply.author_id ,
        board_rereply.board_post_id_id ,
        board_rereply.reply_id_id ,
        board_rereply.body ,
        board_rereply.rereply_image ,
        (select COUNT(board_rereplyrecommend.id) FROM board_rereplyrecommend WHERE board_rereply.id = board_rereplyrecommend.rereply_id_id) AS recommend_count,
        accounts_profile.id ,
        board_reply.id ,
        board_reply.created_at ,
        board_reply.board_post_id_id
        FROM board_rereply 
        INNER JOIN accounts_profile 
            ON ( board_rereply.author_id = accounts_profile.id )
        INNER JOIN board_reply 
            ON ( board_rereply.reply_id_id = board_reply.id )
        WHERE board_rereply.author_id = %s
        ORDER BY board_rereply.id DESC
        LIMIT %s
        OFFSET %s
        """, (request.user.id, limit, start))

    return qs


# [raw sql 완료]
def point_raw_query(request, start, kind, limit=18):
    qs = PointLog.objects.raw('''
        SELECT custom_admin_pointlog.id ,
        custom_admin_pointlog.userid_id ,
        custom_admin_pointlog.param ,
        custom_admin_pointlog.information ,
        custom_admin_pointlog.points
        FROM custom_admin_pointlog
        WHERE custom_admin_pointlog.userid_id = %(author_id)s AND custom_admin_pointlog.param = %(kind)s
        ORDER BY custom_admin_pointlog.id DESC
        LIMIT %(limit)s 
        OFFSET %(start)s
        ''', {'author_id': request.user.id, 'kind': kind, 'limit': limit, 'start': start})

    return qs