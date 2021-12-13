from django.contrib import admin
from .models import *

class Board_postAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'body', 'created_at')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'body', 'board_post_id', 'created_at')

class RereplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'body', 'board_post_id', 'reply_id', 'created_at')

admin.site.register(Board_post, Board_postAdmin)
admin.site.register(Recommend)
admin.site.register(Scrap)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Rereply, RereplyAdmin)
admin.site.register(Replyrecommend)
admin.site.register(Rereplyrecommend)
