from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

from vjit_network.core.models import User, VerificationCode
from vjit_network.api.utils import random_range

OTP_CODE_FROM = settings.OTP_CODE_FROM
OTP_CODE_TO = settings.OTP_CODE_TO
OTP_EXPIRE_TYPE = settings.OTP_EXPIRE_TYPE
OTP_EXPRIE_UNIT = settings.OTP_EXPRIE_UNIT


def calc_otp_expire_time(current: datetime) -> datetime:
    delta = None
    if OTP_EXPIRE_TYPE == 'year':
        delta = timedelta(days=OTP_EXPRIE_UNIT * 360)
    elif OTP_EXPIRE_TYPE == 'month':
        delta = timedelta(days=OTP_EXPRIE_UNIT * 30)
    elif OTP_EXPIRE_TYPE == 'day':
        delta = timedelta(days=OTP_EXPRIE_UNIT)
    elif OTP_EXPIRE_TYPE == 'hour':
        delta = timedelta(hours=OTP_EXPRIE_UNIT)
    elif OTP_EXPIRE_TYPE == 'minute':
        delta = timedelta(minutes=OTP_EXPRIE_UNIT)
    elif OTP_EXPIRE_TYPE == 'second':
        delta = timedelta(seconds=OTP_EXPRIE_UNIT)
    else:
        raise Exception('invalid otp type')
    return timezone.now() + delta


def otp_is_expired(otp_obj: VerificationCode) -> bool:
    return otp_obj.expired_time < timezone.now()


def otp_code_for_user(user: User) -> VerificationCode:
    new_code = random_range(OTP_CODE_FROM, OTP_CODE_TO)
    new_expired_time = calc_otp_expire_time(timezone.now())
    code_obj = None
    try:
        code_obj:  VerificationCode = user.verificationcode
        code_obj.expired_time = new_expired_time
        code_obj.is_enable = True
        code_obj.code = new_code
        code_obj.save()
        return code_obj
    except ObjectDoesNotExist as exc:
        return VerificationCode.objects.create(
            user=user,
            code=new_code,
            expired_time=new_expired_time,
            is_enable=True
        )

