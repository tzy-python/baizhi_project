import random
import re

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from django_redis import get_redis_connection

from edu_api.libs.geetest import GeetestLib
from user.models import UserInfo
from user.utils import get_user_by_account
from user.serializer import UserModelSerializer, MsgLoginSerializer
from edu_api.settings import constants
from edu_api.settings.constants import SMS_EXPIRE_TIME, MOBILE_EXPIRE_TIME
from utils.send_message import Message

pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"


class CaptchaAPIView(APIView):
    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):

        username = request.query_params.get('username')
        user = get_user_by_account(username)
        if user is None:
            return Response({"message": "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')

        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


class UserAPIView(CreateAPIView):
    queryset = UserInfo.objects.all()
    serializer_class = UserModelSerializer


class CheckPhoneAPIView(APIView):
    def get(self, request, mobile):
        if not re.match(r'^1[3-9]\d{9}', mobile):
            return Response({"message": "手机号格式不正确"}, status=http_status.HTTP_400_BAD_REQUEST)
        user = get_user_by_account(mobile)
        if user:
            return Response({"message": "该手机号已被注册"}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response({"message": 'OK'})


class SendMessageAPIView(APIView):

    def get(self, request, mobile):
        # 获取redis连接
        redis_connection = get_redis_connection("sms_code")

        mobile_code = redis_connection.get("sms_%s" % mobile)
        if mobile_code is not None:
            return Response({"message": "您已经在60s内发送过短息了~"}, status=http_status.HTTP_400_BAD_REQUEST)

        # 生成随机的短信验证码
        code = "%06d" % random.randint(0, 999999)

        # 3. 将验证码保存到redis中
        redis_connection.setex("sms_%s" % mobile, SMS_EXPIRE_TIME, code)  # 60s不允许再发送
        redis_connection.setex("mobile_%s" % mobile, MOBILE_EXPIRE_TIME, code)  # 验证码的有效时间

        # 4. 调用方法  完成短信的发送
        try:
            # from my_task.msg.tasks import send_sms
            # send_sms.delay(mobile,code)
            message = Message(constants.API_KEY)
            message.send_message(mobile, code)
        except:
            return Response({"message": "短信发送失败"}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "发送短信成功"}, status=http_status.HTTP_200_OK)

from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
def create_token(user):
    return jwt_encode_handler(jwt_payload_handler(user))


class SmsLoginAPIView(APIView):

    def post(self,request,*args,**kwargs):
        mobile = request.data.get("mobile")
        sms = request.data.get("sms")
        print("sms",sms)
        try:
            user = UserInfo.objects.get(phone=mobile)
            redis_connection = get_redis_connection("sms_code")
            mobile_code = redis_connection.get("sms_%s" % mobile)
            print("mobile_code",mobile_code.decode())
            if sms == mobile_code.decode():
                user.token = create_token(user)
                return Response(MsgLoginSerializer(user).data)
            else:
                return Response({"message":"验证码错误"},status=http_status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message":"用户不存在"},status=http_status.HTTP_400_BAD_REQUEST)
