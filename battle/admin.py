from django.contrib import admin
from .models import *

class VoteBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'start_datetime', 'end_datetime', 'created_at')

class VoteItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'item_content', 'item_image', 'created_at')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

class VoteBoardReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'created_at')

class VoteBoardRereplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'created_at')

class VoteBoardReplyRecommendAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

class VoteBoardRereplyRecommendAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')


admin.site.register(VoteBoard, VoteBoardAdmin)
admin.site.register(VoteItem, VoteItemAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(VoteBoardReply, VoteBoardReplyAdmin)
admin.site.register(VoteBoardRereply, VoteBoardRereplyAdmin)
admin.site.register(VoteBoardReplyRecommend, VoteBoardReplyRecommendAdmin)
admin.site.register(VoteBoardRereplyRecommend, VoteBoardRereplyRecommendAdmin)
