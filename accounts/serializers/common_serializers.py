from rest_framework import serializers
from accounts.models import Profile


# 댓글에서 작성자 정보 보여주기
class ReplyShowProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    profile_image = serializers.ImageField(required=False,)

    class Meta:
        model = Profile
        fields = ("nickname", "profile_image",)


# 게시글에서 작성자 정보 보여주기
class BoardShowProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField()
    introduction = serializers.CharField(max_length=300, required=False,)
    profile_image = serializers.ImageField(required=False,)

    class Meta:
        model = Profile
        fields = ("nickname", "introduction", "profile_image",)




