from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _


@deconstructible
class NewASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^[a-z0-9]+$'
    message = _(
        '아이디는 영문 소문자, 숫자만 사용할 수 있습니다.(영문 대문자, 특수기호 사용 불가)'
    )
    

@deconstructible
class NicknameValidator(validators.RegexValidator):
    regex = r'^[ㄱ-ㅎㅏ-ㅣ가-힣\w]+$'
    message = _(
        '닉네임은 한글/영문/숫자만 사용할 수 있습니다.(특수기호 사용 불가)'
    ) 
