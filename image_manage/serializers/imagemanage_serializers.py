from rest_framework import serializers

from image_manage.models import BoardImage


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardImage
        fields = ("image",)
