from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import serializers

from accounts.models import Profile
from custom_admin.models import Blacklist

import datetime


class BlackListSerializer(serializers.ModelSerializer):
    userid = serializers.CharField()
    nickname = serializers.SerializerMethodField(read_only=True)
    # 남은 제제 일수
    ban_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blacklist
        fields = (
            "id", "userid", "nickname",
            "created_at", "updated_at",
            "ban_duration", "ban_left"
        )

    @transaction.atomic
    def create(self, validated_data):
        # 생성 시
        # 쿼리 가져오기
        qs = get_object_or_404(Profile, username=validated_data["userid"])
        # userid 대입하기
        validated_data['userid'] = qs
        # 만약 있을 경우 update 하기
        check_blacklist = Blacklist.objects.filter(userid__username=validated_data["userid"])

        if check_blacklist.exists():
            blacklist = get_object_or_404(Blacklist, userid__username=validated_data["userid"])
            blacklist.ban_duration = validated_data["ban_duration"]
            blacklist.save()
        # 없을 경우 생성시키기
        else:
            blacklist = Blacklist.objects.create(**validated_data)
        # 없을 경우 새로생성 하기
        return blacklist

    def get_nickname(self, obj):
        return obj.userid.nickname

    def get_ban_left(self, obj):
        make_day = datetime.timedelta(days=obj.ban_duration) - (datetime.datetime.now() - obj.updated_at)
        if make_day.days + 1 < 1:
            return False
        return make_day.days + 1


class BlackUserSerializer(serializers.ModelSerializer):
    userid = serializers.CharField()
    nickname = serializers.SerializerMethodField(read_only=True)
    # 남은 제제 일수
    ban_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blacklist
        fields = (
            "userid", "nickname",
            "created_at", "updated_at",
            "ban_duration", "ban_left"
        )

    def get_nickname(self, obj):
        return obj.userid.nickname

    def get_ban_left(self, obj):
        make_day = datetime.timedelta(days=obj.ban_duration) - (datetime.datetime.now() - obj.updated_at)
        if make_day.days + 1 < 1:
            return False
        return make_day.days + 1
