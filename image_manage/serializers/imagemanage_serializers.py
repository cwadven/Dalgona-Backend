from rest_framework import serializers
from rest_framework.exceptions import APIException

from image_manage.models import BoardImage


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardImage
        fields = ("image",)

    def validate_image(self, value):
        size = value.size
        if size and (size // 1024) > 3000:
            raise APIException("이미지 최대 용량 3MB를 초과했습니다.")
        return value
