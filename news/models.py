from django.db import models


class NewsData(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    image = models.ImageField(upload_to='news_image/', null=False, blank=False)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 정렬 기준 important 순 및 이름 순
        ordering = ('-date',)

    def __str__(self): 
        return self.title


class PopularKeyword(models.Model):
    word = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.word
