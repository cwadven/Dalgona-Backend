from django.contrib import admin
from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname')


admin.site.register(Profile, ProfileAdmin)
