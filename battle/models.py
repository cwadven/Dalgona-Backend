from django.db import models
from django.conf import settings


# 아이템이 들어가야하는 공간
class VoteBoard(models.Model):
    title = models.CharField(max_length=50, db_index=True)
    content = models.TextField()
    board_image = models.ImageField(upload_to='voteboard_image/', null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return '%s' % self.title


# 투표할 아이템
class VoteItem(models.Model):
    voteboard_id = models.ForeignKey(VoteBoard, on_delete=models.CASCADE, related_name='voteitem')
    item_name = models.CharField(max_length=30)
    item_content = models.TextField()
    item_image = models.ImageField(upload_to='voteitem_image/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id


# 투표
class Vote(models.Model):
    voteboard_id = models.ForeignKey(VoteBoard, on_delete=models.CASCADE)
    voteitem_id = models.ForeignKey(VoteItem, on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id


 # VoteBoard의 댓글
class VoteBoardReply(models.Model):
    voteboard_id = models.ForeignKey(VoteBoard, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    anonymous = models.BooleanField(default=False)
    votereply_image = models.ImageField(upload_to='votereply_image/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id


# VoteBoard의 댓글 추천
class VoteBoardReplyRecommend(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    voteboardreply_id = models.ForeignKey(VoteBoardReply, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id


# VoteBoard의 대댓글
class VoteBoardRereply(models.Model):
    voteboard_id = models.ForeignKey(VoteBoard, on_delete=models.CASCADE)
    voteboardreply_id = models.ForeignKey(VoteBoardReply, related_name='voteboardrereply', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    anonymous = models.BooleanField(default=False)
    voterereply_image = models.ImageField(upload_to='voterereply_image/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id


# VoteBoard의 대댓글 추천
class VoteBoardRereplyRecommend(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    voteboardrereply_id = models.ForeignKey(VoteBoardRereply, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.id
