from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from django.contrib.auth.models import AbstractUser
# Create your models here.

from . import constants


class User(AbstractUser):
    """重写django自带的User模型类"""

    # 添加mobile字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def generate_send_sms_token(self):
        """
        生成发送短信验证码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        data = {'mobile': self.mobile}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验发送短信验证码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')

    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True

    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html/?token=' + token
        return verify_url

    @staticmethod
    def check_email_verify_token(token):
        """access_token校验"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.EMAIL_VERIFY_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            email = data.get('email')
            user_id = data.get("user_id")
            # user = User.objects.get(id=user_id, email=email)
            # user.email_active = True
            # user.save()
            User.objects.filter(id=user_id, email=email).update(email_active=True)
            return True




























