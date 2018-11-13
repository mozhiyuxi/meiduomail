from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated

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


# 校验手机验证码，向用户返回access_token
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


# 重置密码
class ResetPasswordView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = serializers.ResetPasswordSerializer
    queryset = User.objects.all()

    def post(self, request, pk):
        self.update(request, pk)


# 用户个人中心
class UserDetailView(RetrieveAPIView):
    """个人中心"""
    # 此页面需要权限校验
    pagination_class = [IsAuthenticated]
    serializer_class = serializers.UserDetailSerializer

    # 1. 重写get_object()方法，通过token获取登陆的模型类对象
    def get_object(self):
        return self.request.user




# 发送激活邮件
class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    def get_object(self):
        pass

    # 为了是视图的create方法在对序列化器进行save操作时执行序列化器的update方法，更新user的email属性
    # 所以重写get_serializer方法，在构造序列化器时将请求的user对象传入
    # 注意：在视图中，可以通过视图对象self中的request属性获取请求对象
    def get_serializer(self, *args, **kwargs):
        return serializers.EmailSerializer(self.request.user, data=self.request.data)


class EmailVerifyView(APIView):
    """邮箱验证"""
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验  保存
        result = User.check_email_verify_token(token)

        if result:
            return Response({"message": "OK"})
        else:
            return Response({"非法的token"}, status=status.HTTP_400_BAD_REQUEST)
