import datetime

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.utils import timezone

from rest_framework import permissions
from allauth.account.admin import EmailAddress
from rest_framework.exceptions import APIException

from custom_admin.models import Blacklist


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_superuser)


# 이메일 인증했는지 확인하는 permission 적용 완료!
class IsEmailAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user and EmailAddress.objects.filter(user=request.user, verified=True).exists())


# # Board 앱
# # 슈퍼 유저 까지 가능하도록 설정
class IsOwnerOrSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the Board.
        return obj.author == request.user or request.user.is_superuser


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsPureUser(permissions.BasePermission):
    message = 'This user is in blacklist'

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return True
        if request.user.is_superuser:
            return True
        with transaction.atomic():
            qs = Blacklist.objects.filter(userid__id=request.user.id)
            if qs.exists():
                for ban_log in qs:
                    if ban_log.updated_at + datetime.timedelta(days=ban_log.ban_duration) >= timezone.datetime.now():
                        return False
                    else:
                        ban_log.delete()
        return True


class LowWritePriority(APIException):
    status_code = 401
    default_detail = 'User level is low to write a post.'