# 序列化对象
from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

from meiduo_backend.utils.exception import logger


# 短信验证码
class SmsCodeSerializer(serializers.Serializer):
    """图片验证码校验"""
    # 1. 定义字段
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        """校验"""
        image_code_id = attrs["image_code_id"]
        text = attrs["text"]

        # redis查询真实图片验证码
        # 1. 创建redis对象
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get("img_%s" % image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        # 验证结束后删除图片验证码
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as ret:
            logger.error(ret)

        # 比较图片验证码
        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误")

        # 判断是否在60s内
        try:
            mobile = self.context['view'].kwargs['mobile']
        except KeyError:
            mobile = None
        # 通过视图是否有mobile参数判断是否进行短信测操作
        if mobile:
            send_flag = redis_conn.get("send_flag_%s" % mobile)
            if send_flag:
                raise serializers.ValidationError('请求次数过于频繁')

        return attrs
