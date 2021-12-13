from rest_framework import generics
from rest_framework import viewsets

from custom_admin.models import Blacklist

from custom_admin.serializers.cmsblack_serializers import BlackListSerializer, BlackUserSerializer

from common.permissions import IsSuperUser


class BlackListViewset(generics.ListCreateAPIView):
    queryset = Blacklist.objects.all()
    serializer_class = BlackListSerializer
    permission_classes = (IsSuperUser,)


class BlackUserViewset(viewsets.ModelViewSet):
    queryset = Blacklist.objects.all()
    serializer_class = BlackUserSerializer
    permission_classes = (IsSuperUser,)
