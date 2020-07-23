import xadmin
from order.models import Order, OrderDetail


class OrderModelAdmin(object):
    """订单模型"""
    pass


xadmin.site.register(Order, OrderModelAdmin)


class OrderDetailAdmin(object):
    """订单详情模型"""
    pass


xadmin.site.register(OrderDetail, OrderDetailAdmin)
