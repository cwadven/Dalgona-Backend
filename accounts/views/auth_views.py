import datetime
import requests

from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import generics, status

from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC, EmailAddress
from allauth.account.utils import send_email_confirmation
from rest_auth.views import PasswordResetView
from rest_auth.registration.views import RegisterView

from accounts.models import Profile
from accounts.serializers.auth_serializers import (
    UsernameOverlapSerializer, EmailOverlapSerializer, NicknameOverlapSerializer,
    UsernameEmailAddressSerializer, EmailToUsernameSerializer, NewPasswordResetSerializer
)

from common.iamport import get_token


# 회원가입 하기
class RegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        access_token = get_token()
        imp_uid = request.POST.get('imp_uid', False)

        if imp_uid and access_token:
            # 정말로 그 유저인지 판단
            url = f'https://api.iamport.kr/certifications/{imp_uid}'
            headers = {"Authorization": access_token}

            req = requests.get(url, headers=headers)
            req.raise_for_status
            res = req.json()

            if res['response']:
                if res['response']['certified']:
                    cur_age_time = timezone.datetime.now() - datetime.datetime.strptime(res['response']['birthday'], '%Y-%m-%d')
                    if cur_age_time.days//365 >= 14:
                        # 이미 있는 유저인지 확인
                        qs = Profile.objects.filter(unique_key=res['response']['unique_key'])
                        if not qs.exists():
                            serializer = self.get_serializer(data=request.data)
                            serializer.is_valid(raise_exception=True)
                            user = self.perform_create(serializer)
                            headers = self.get_success_headers(serializer.data)

                            return Response(self.get_response_data(user),
                                            status=status.HTTP_201_CREATED,
                                            headers=headers)
                        else:
                            return Response({"error": f"이미 {qs[0].email} 로 가입한 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error": "만 14세 미만입니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "인증되지 않은 사용자 입니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "인증결과가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "처리 중 문제가 있었습니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)


# 휴대폰 인증 관련 (인증 정보 조회 후, 전달)
class PhoneCertificationView(APIView):
    def post(self, request, *args, **kwargs):
        access_token = get_token()
        imp_uid = request.POST.get('imp_uid', False)
        find = request.POST.get('find', False)

        if imp_uid and access_token:
            url = f'https://api.iamport.kr/certifications/{imp_uid}'
            headers = {"Authorization": access_token}

            req = requests.get(url, headers=headers)
            res = req.json()

            if res['response']:
                if res['response']['certified']:
                    # 만 14세 나이
                    cur_age_time = timezone.datetime.now() - datetime.datetime.strptime(res['response']['birthday'], '%Y-%m-%d')
                    if cur_age_time.days//365 >= 14:
                        # 이미 있는 유저인지 확인
                        qs = Profile.objects.filter(unique_key=res['response']['unique_key'])
                        if qs.exists():
                            # 아이디/비밀번호 찾기 와 회원가입 분기
                            if not find:
                                return Response(
                                    {"error": f"이미 {qs[0].email} 로 가입한 사용자입니다."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            else:
                                context = {
                                    "imp_uid": imp_uid,
                                }
                                return Response(context, status=status.HTTP_202_ACCEPTED)
                        else:
                            # 아이디/비밀번호 찾기 와 회원가입 분기
                            if not find:
                                context = {
                                    "imp_uid": imp_uid,
                                    "unique_key": res['response']['unique_key'],
                                    "gender": res['response']['gender'],
                                    "birthday" : res['response']['birthday'],
                                }
                                return Response(context, status=status.HTTP_202_ACCEPTED)
                            else:
                                return Response({"error": f"존재하지 않은 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error": "만 14세 미만입니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "인증되지 않은 사용자 입니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "인증결과가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "처리 중 문제가 있었습니다! 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)


# 다날 아이디/비밀번호 찾기 (인증 정보 조회 후, 전달)
class PhoneCertificationFindView(APIView):
    def post(self, request, *args, **kwargs):
        access_token = get_token()
        imp_uid = request.POST.get('imp_uid', False)
        new_password = request.POST.get('new_password', False)

        if imp_uid and access_token:
            url = f'https://api.iamport.kr/certifications/{imp_uid}'
            headers = { "Authorization": access_token }

            req = requests.get(url, headers=headers)
            res = req.json()

            if res['response']:
                if res['response']['certified']:
                    # 만 14세 나이
                    cur_age_time = timezone.datetime.now() - datetime.datetime.strptime(res['response']['birthday'], '%Y-%m-%d')
                    if cur_age_time.days//365 >= 14:
                        # 이미 있는 유저인지 확인
                        qs = Profile.objects.filter(unique_key=res['response']['unique_key'])
                        if qs.exists():
                            if not new_password:
                                return Response({"success": f"{qs[0].username}"}, status=status.HTTP_202_ACCEPTED)
                            else:
                                # 비밀번호 수정하기 위한 new_password 수정
                                qs[0].set_password(new_password)
                                qs[0].save()
                                return Response({"success": f"비밀번호를 수정하셨습니다."}, status=status.HTTP_202_ACCEPTED)
                        else:
                            return Response({"success": f"가입한 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error": "만 14세 미만입니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "인증되지 않은 사용자 입니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "인증결과가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "처리 중 문제가 있었습니다! 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 불필요]
# 메일 인증 처리
class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        try:
            confirmation.confirm(self.request)
        except Exception as e:
            # 인증 실패했습니다!
            return Response(
                data={"detail": "something get wrong"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # A React Router Route will handle the failure scenario
        # 인증 성공했습니다!
        # 인증 성공 시, 사용자 닉네임 보여주기
        query = EmailAddress.objects.get(email=self.object.email_address)
        return Response(
            data={"detail": "Email verified", "nickname": query.user.nickname},
            status=status.HTTP_202_ACCEPTED
        )

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                # A React Router Route will handle the failure scenario
                return HttpResponseRedirect('/login/failure/')
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs


# [쿼리 최적화 불필요]
# 이메일 재 전송 인증 보내기
class ReEmailConfirmation(generics.CreateAPIView):
    queryset = EmailAddress.objects.all()
    serializer_class = UsernameEmailAddressSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        # 해당 이메일에서 회원가입한 닉네임으로 인증 보내버리기!!
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            qs = self.get_queryset().filter(user__username=username, verified=True).exists()
            if qs:
                return Response({'detail': 'Email already verified'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            # 그런 후 해당 아이디를 같은 Profile 찾고 있을 경우 이메일 전송하기
            try:
                # 재인증하는 이메일이 기존에 존재하는 이메일이면
                if self.get_queryset().filter(
                        user__username=username,
                        email=serializer.validated_data["email"]
                ).exists():
                    pass
                else:
                    # 다른 사람 이메일과 중복한 이메일이 있는 지 확인
                    if self.get_queryset().filter(email=serializer.validated_data["email"]).exists():
                        return Response({'detail': 'Email already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                # 전 이메일과 동일하지 않고 새로운 이메일이면 이메일 수정
                if self.get_queryset().get(user__username=username).email != serializer.validated_data["email"]:
                    new_email = self.get_queryset().get(user__username=username)
                    # 이메일 변경 함수
                    new_email.change(request, serializer.validated_data["email"], confirm=False)

                user = Profile.objects.get(username=username)
                # 이메일 전송
                send_email_confirmation(request, user)
                # 재인증 시 이메일 주소 넣기
                email_add = self.get_queryset().get(user__username=username)
                return Response({'detail': 'Email confirmation sent', 'email':email_add.email}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': 'User not exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
# 아이디 중복확인하기
class UsernameOverlap(generics.CreateAPIView):
    serializer_class = UsernameOverlapSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response(data={"detail":["this username is unique"]}, status=status.HTTP_200_OK)
        else:
            detail = dict()
            detail["detail"] = serializer.errors["username"]
            return Response(data=detail, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
# 이메일 중복확인하기
class EmailOverlap(generics.CreateAPIView):
    serializer_class = EmailOverlapSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response(data={"detail":["this email is unique"]}, status=status.HTTP_200_OK)
        else:
            detail = dict()
            detail["detail"] = serializer.errors["email"]
            return Response(data=detail, status=status.HTTP_400_BAD_REQUEST)


# [쿼리 최적화 완료]
# 닉네임 중복확인하기
class NicknameOverlap(generics.CreateAPIView):
    serializer_class = NicknameOverlapSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response(data={"detail":["this nickname is unique"]}, status=status.HTTP_200_OK)
        else:
            detail = dict()
            detail["detail"] = serializer.errors["nickname"]
            return Response(data=detail, status=status.HTTP_400_BAD_REQUEST)


# 이메일로 아이디 검색
class EmailToUsernameView(generics.CreateAPIView):
    serializer_class = EmailToUsernameSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email_address = serializer.validated_data['email']
            qs = EmailAddress.objects.filter(email=email_address)
            if qs.exists():
                user = qs.get().user
                nickname = user.nickname
                username = user.username
                send_email = EmailMessage("[DALGONA] " + nickname + "님의 ID", "회원님의 ID는 " + username + " 입니다.", to=[email_address])
                send_email.send()
                 
                return Response({"result": "이메일을 전송했습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({"result": "입력한 이메일에 해당하는 회원 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 수정
class NewPasswordResetView(PasswordResetView):
    serializer_class = NewPasswordResetSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email_address = serializer.validated_data['email']
            email_qs = EmailAddress.objects.filter(email=email_address)
            check_user = serializer.validated_data['username']
            username_qs = Profile.objects.filter(username=check_user)
            if email_qs.exists() and username_qs.exists():
                user = email_qs.get().user
                check = username_qs.get()
                if user == check:
                    serializer.save()
                    return Response({"result": "이메일을 전송했습니다."}, status=status.HTTP_200_OK)
                else:
                    return Response({"result": "이메일과 아이디가 동일한 회원의 정보가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"result": "입력한 이메일과 아이디에 해당하는 회원정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
