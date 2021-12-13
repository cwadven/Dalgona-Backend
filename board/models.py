from django.db import models
from board_list.models import Board_list, Category
from django.conf import settings

from django.utils.functional import cached_property


# 추상 클래스로 생성 및 업데이트
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

# 게시글
class Board_post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    board_url = models.ForeignKey(Board_list, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=35, blank = False, null=False, db_index=True)
    body = models.TextField()
    views = models.IntegerField(default=0)
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return '%s' % (self.id)

# 글 추천
class Recommend(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    board_post_id = models.ForeignKey(Board_post, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % (self.board_post_id)

# 스크랩
class Scrap(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    board_post_id = models.ForeignKey(Board_post, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % (self.board_post_id)

# 댓글
class Reply(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    board_post_id = models.ForeignKey(Board_post, on_delete=models.CASCADE)
    body = models.TextField()
    anonymous = models.BooleanField(default=False)
    reply_image = models.ImageField(upload_to='reply_image/', null=True, blank=True)

    def __str__(self):
        return '%s' % (self.id)

# 댓글 추천
class Replyrecommend(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reply_id = models.ForeignKey(Reply, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % (self.reply_id)


# 대댓글
class Rereply(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    board_post_id = models.ForeignKey(Board_post, on_delete=models.CASCADE)
    reply_id = models.ForeignKey(Reply, related_name='rereply', on_delete=models.CASCADE)
    body = models.TextField()
    anonymous = models.BooleanField(default=False)
    rereply_image = models.ImageField(upload_to='rereply_image/', null=True, blank=True)

    def __str__(self):
        return '%s' % (self.id)


class Rereplyrecommend(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    rereply_id = models.ForeignKey(Rereply, on_delete=models.CASCADE)

    
    def __str__(self):
        return '%s' % (self.rereply_id)
