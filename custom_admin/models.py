from django.db import models
from accounts.models import Profile

# 트랜잭션
from django.db import transaction


class Blacklist(models.Model):
    userid = models.ForeignKey(Profile, related_name='bad_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ban_duration = models.IntegerField(default=7)

    def __str__(self):
        return '%s' % self.userid.username


# 포인트
class PointLog(models.Model):
    PARAM_CHOICES = (
        ('G', 'GET'),
        ('U', 'USE'),
        ('D', 'LOSE'),
    )
    userid = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # 어느 종류에서 받거나 삭제되는 것인지
    kind = models.CharField(max_length=30)
    # 포인트 추가인지 삭제인지
    param = models.CharField(max_length=1, choices=PARAM_CHOICES, db_index=True)
    # 어느 종류의 id 인지 확인하여 추후에 악의적인 사용자
    # 바로 삭제하거나 생성하는 경우를 막기 위해서
    kindid = models.IntegerField(blank=True, null=True)
    information = models.TextField()
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.userid.username

    # 추후에 생성 했을 경우 바로 자장하기 위해서
    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                user = self.userid
                # 얻거나 포인트를 잃을 경우
                if self.param == 'G':
                    user.points = user.points + self.points
                elif self.param == 'U':
                    user.points = user.points - self.points
                elif self.param == 'D':
                    user.points = user.points - self.points
                user.save()
        except:
            pass

        return super(PointLog, self).save(*args, **kwargs)
