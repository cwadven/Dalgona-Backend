from rest_framework.response import Response
from rest_framework import status

from image_manage.serializers.imagemanage_serializers import UploadImageSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework import generics


# 이미지 업로드
class UploadImageView(generics.CreateAPIView):
    serializer_class = UploadImageSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
