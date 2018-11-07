from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins

from . import serializers
from .models import User


# 校验用户名是否已被注册
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# 校验手机号是否已被注册
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# 注册用户
class CreateUserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class PasswordTokenView(GenericAPIView):
    """
    用户帐号设置密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        """
        根据用户帐号获取修改密码的token
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})

class ResetPasswordView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = serializers.ResetPasswordSerializer
    queryset = User.objects.all()

    def post(self, request, pk):
        self.update(request, pk)
