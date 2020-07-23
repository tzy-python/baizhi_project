from edu_api.settings import constants
from edu_api.util.send_message import Message
from my_task.main import app
import logging

logger = logging.getLogger('django')

# celery的任务必须写在tasks文件中，别的文件名不识别

@app.task(name="send_sms")  # name可以指定当前任务的名称
def send_sms(mobile,code):
    print("发送验证码")
    message = Message(constants.API_KEY)
    status = message.send_message(mobile, code)
    if not status:
        logger.error("用户发送短信失败，手机号为：%s" % mobile)
    return "111"


@app.task(name="send_mail")
def send_mail():
    print("发邮件")
    return "邮件"
