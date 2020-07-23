from datetime import datetime
from django.db import transaction

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django_redis import get_redis_connection

from course.models import CourseExpire, Course
from order.models import Order, OrderDetail


class OrderModelSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_number", "pay_type")

        extra_kwargs = {
            "id": {"read_only": True},
            "order_number": {"read_only": True},
            "pay_type": {"write_only": True}
        }

    def validate(self, attrs):
        pay_type = attrs.get("pay_type")
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("请选择合理的支付方式")
        return attrs

    def create(self, validated_data):
        """生成订单与订单详情"""
        redis_connection = get_redis_connection("cart")
        # 通过context获取到request对象
        user_id = self.context["request"].user.id
        incr = redis_connection.incr("order")

        # 生成唯一的订单号  时间戳  用户id  随机字符串
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%06d" % incr

        with transaction.atomic():

            # 记录下事务回滚的点
            rollback_id = transaction.savepoint()

            # 生成订单
            order = Order.objects.create(
                order_title="我是订单标题",
                total_price=0,
                real_price=0,
                order_number=order_number,
                order_status=0,
                pay_type=validated_data.get("pay_type"),
                credit=0,
                coupon=0,
                order_desc="这是一个订单",
                user_id=user_id
            )

            # 生成订单详情
            # 获取当前用户购物车中所有的商品
            cart_list = redis_connection.hgetall("cart_%s" % user_id)
            select_list = redis_connection.smembers("selected_%s" % user_id)

            for course_id_byte, expire_id_byte in cart_list.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_id_byte)

                # 判断商品id是否在已勾选的列表中
                if course_id_byte in select_list:

                    try:
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        transaction.savepoint_rollback(rollback_id)
                        return serializers.ValidationError("当前商品不存在")

                    # 如果有效期的id大于0  则需计算商品的价格  id不大于0则永久有效
                    original_price = course.price
                    try:
                        if expire_id > 0:
                            course_expire = CourseExpire.objects.get(id=expire_id)
                            # 对应有效期的价格
                            original_price = course_expire.price
                            expire_text = course_expire.expire_text
                    except CourseExpire.DoesNotExist:
                        transaction.savepoint_rollback(rollback_id)
                    # 根据已勾选的商品对应的有效期的价格去计算勾选商品的最终价格
                    real_expire_price = course.real_expire_price(expire_id)
                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=original_price,
                            real_price=real_expire_price,
                            discount_name=course.discount_name
                        )
                    except:
                        raise serializers.ValidationError("订单生成失败")

                    # 计算订单总价
                    order.total_price += float(original_price)
                    order.real_price += float(real_expire_price)
                    redis_connection.hdel("cart_%s" % user_id, course_id)
                    redis_connection.srem("selected_%s" % user_id, course_id)
                order.save()
            return order
