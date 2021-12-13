from django.contrib import admin

from news.models import NewsData, PopularKeyword


admin.site.register(NewsData)
admin.site.register(PopularKeyword)
