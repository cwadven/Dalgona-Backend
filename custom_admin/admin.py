from django.contrib import admin
from .models import *

class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('userid', 'ban_duration', 'created_at')

admin.site.register(Blacklist, BlacklistAdmin)
admin.site.register(PointLog)