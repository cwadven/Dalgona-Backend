from rest_framework import serializers

from rest_framework.validators import UniqueValidator

from common.validators import NewASCIIUsernameValidator, NicknameValidator

# PointLog
from custom_admin.models import *

# 비밀번호 찾기
from rest_auth.serializers import PasswordResetSerializer


# 아이디를 통해서 이메일 전송하기 (username)
class UsernameEmailAddressSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=5, max_length=20)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ("username", "email")


# 중복확인 (username)
class UsernameOverlapSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        min_length=5,
        max_length=20,
        validators=[UniqueValidator(queryset=Profile.objects.all()), NewASCIIUsernameValidator()]
    )

    class Meta:
        model = Profile
        fields = ("username",)


# 중복확인 (email)
class EmailOverlapSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Profile.objects.all())]
    )

    class Meta:
        model = Profile
        fields = ("email",)


# 중복확인 (nickname)
class NicknameOverlapSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(
        required=True,
        min_length=1,
        max_length=20,
        validators=[UniqueValidator(queryset=Profile.objects.all()), NicknameValidator()]
    )

    class Meta:
        model = Profile
        fields = ("nickname",)


# email 찾기
class EmailToUsernameSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


# 비밀번호 reset
class NewPasswordResetSerializer(PasswordResetSerializer):
    username = serializers.CharField(required=True)

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {
            "email_template_name": "registration/new_password_reset_email.html",
            "subject_template_name": "registration/new_password_reset_subject.html"
        }
