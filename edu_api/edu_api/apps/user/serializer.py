import re
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from django.core.cache import cache

from user.models import UserInfo
from user.utils import get_user_by_account


class UserModelSerializer(ModelSerializer):
    token = serializers.CharField(max_length=500, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = UserInfo
        fields = ("id", 'username', 'password', 'phone', 'token', "sms_code")

        extra_kwargs = {
            "id": {
                "read_only": True
            },
            "username": {
                "read_only": True
            },
            "password": {
                "write_only": True
            },
            "phone": {
                "write_only": True
            }
        }

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        sms_code = attrs.get("sms_code")
        print(sms_code)

        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式有误")

        try:
            user = get_user_by_account(phone)
        except:
            user = None
        if user:
            raise serializers.ValidationError("该手机号已被注册")

        #  验证手机号短信验证码是否正确
        redis_connection = get_redis_connection("sms_code")
        phone_code = redis_connection.get("mobile_%s" % phone)
        if phone_code.decode() != sms_code:
            raise serializers.ValidationError("验证码不一致")
        # 删除验证码
        else:
            cache.delete_pattern("mobile_%s" % phone)

        return attrs

    def create(self, validated_data):
        pwd = validated_data.get("password")
        hash_pwd = make_password(pwd)
        username = validated_data.get("phone")
        user = UserInfo.objects.create(
            username=username,
            phone=username,
            password=hash_pwd
        )

        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)

        return user


class MsgLoginSerializer(ModelSerializer):
    token = serializers.CharField(max_length=500, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = UserInfo
        fields = ("id", "phone", "token", "sms_code")

        extra_kwargs = {
            "id": {
                "read_only": True
            },
            "phone": {
                "read_only": True
            }
        }

    def validate(self, attrs):
        phone = attrs.get("mobile")
        sms_code = attrs.get("sms")

        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式有误")

        try:
            user = get_user_by_account(phone)
        except:
            user = None
        if user:
            redis_connection = get_redis_connection("sms_code")
            phone_code = redis_connection.get("mobile_%s" % phone)
            if phone_code.decode() != sms_code:
                raise serializers.ValidationError("验证码不一致")
            else:
                cache.delete_pattern("mobile_%s" % phone)
        return attrs
