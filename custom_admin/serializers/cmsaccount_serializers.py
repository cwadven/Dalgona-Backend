import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import Profile
from custom_admin.models import Blacklist


class AccountListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("username", "level", "nickname", "points", "date_joined", "last_login",)


class AccountProfileSerializer(serializers.ModelSerializer):
    # 사용자 금지 시간
    ban = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("nickname", "level", "introduction", "date_joined", "profile_image", "points", "ban")

    def get_ban(self, obj):
        qs = Blacklist.objects.filter(userid__username=obj.username)
        if qs.exists():
            for instance in qs:
                make_day = datetime.timedelta(days=instance.ban_duration) + (instance.updated_at)
                if make_day < datetime.datetime.now():
                    return False
                else:
                    return make_day
        else:
            return False


# 관리자 회원 정보 수정
class AdminAccountUpdateSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(
        required=False,
        min_length=1,
        max_length=20,
        validators=[UniqueValidator(queryset=Profile.objects.all())]
    )
    introduction = serializers.CharField(max_length=300, required=False,)
    profile_image = serializers.ImageField(required=False,)

    class Meta:
        model = Profile
        fields = ("nickname", "introduction", "profile_image", "points", "level")