import random
import logging
import re

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView, CreateAPIView

# Create your views here.
from meiduo_backend.apps.verification import constants, serializers
from meiduo_backend.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code

# 生成logger生成器
from users.models import User
from users.utils import get_user_by_account

logger = logging.getLogger("django")


# 图片验证码视图
class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self, request, image_code_id):
        """
        获取图片验证码
        """

        # 生成验证码图片
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")


# 短信验证码
class SmsCodes(GenericAPIView):
    """短信验证码"""
    serializer_class = serializers.SmsCodeSerializer

    def get(self, request, mobile):
        """
        创建短信验证码
        """
        # 判断图片验证码, 判断是否在60s内
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        logger.debug(sms_code)

        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信验证码
        # sms_code_expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        # ccp = CCP()
        # status = ccp.send_template_sms(mobile, [sms_code, sms_code_expires], constants.SMS_CODE_TEMP_ID)
        # print(status)
        # 使用celery多任务操作
        # send_sms_code.delay(mobile, sms_code)

        return Response({"message": "OK"})


# 忘记密码校验图片验证码
class SMSCodeTokenView(GenericAPIView):
    serializer_class = serializers.SmsCodeSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 验证完成，向前端返回accesstoken
        user = get_user_by_account(account)
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 生成发送短信的access_token
        access_token = user.generate_send_sms_token()

        # 处理手机号
        mobile = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', user.mobile)
        return Response({'mobile': mobile, 'access_token': access_token})


class SMSCodeByTokenView(APIView):
    """
    短信验证码
    """
    def get(self, request):
        """
        凭借token发送短信验证码
        """
        # 验证access_token
        access_token = request.query_params.get('access_token')
        if not access_token:
            return Response({'message': '缺少access token'}, status=status.HTTP_400_BAD_REQUEST)
        mobile = User.check_send_sms_code_token(access_token)
        if not mobile:
            return Response({'message': 'access token无效'}, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否在60s内
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return Response({"message": "请求次数过于频繁"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        print("短信验证码------------->", sms_code)

        # 保存短信验证码与发送记录
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信验证码
        send_sms_code.delay(mobile, sms_code)

        return Response({"message": "OK"}, status.HTTP_200_OK)

