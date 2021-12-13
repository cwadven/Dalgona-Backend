from django.db import models
class Board_list(models.Model):
    id = models.AutoField(primary_key=True)
    board_name = models.CharField(max_length=20, unique=True, blank=False, null=False)
    board_url = models.SlugField(max_length=30, unique=True, blank=False, null=False)
    division = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    introduction = models.TextField(default='', null=True, blank=True)
    write_priority = models.IntegerField(default=-1, null=False)
    read_priority = models.IntegerField(default=-1, null=False)

    class Meta:
        # 정렬 기준 important 순 및 이름 순
        ordering = ('-division','board_name',)

    def __str__(self):
        return '%s' % (self.board_url)
        
class Category(models.Model):
    category_name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 역참조 하기 위해서는 related_name 추가
    board_url = models.ForeignKey(Board_list, related_name='category', on_delete=models.CASCADE,)
    def __str__(self):
        return '%s' % (self.category_name)


