# 任务文件，main会自行找到包中的相应函数

from .yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信任务
    :param mobile: 手机号
    :param sms_code: 验证码
    :return: None
    """
    # 发送短信
    sms_code_expires = constants.SMS_CODE_REDIS_EXPIRES // 60
    ccp = CCP()
    status = ccp.send_template_sms(mobile, [sms_code, sms_code_expires], constants.SMS_CODE_TEMP_ID)
