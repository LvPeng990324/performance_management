# 用于获取queryset数据类型具体数据的过滤器文件
from django.template import Library
import datetime

# 将注册类实例化为register对象
register = Library()


# 获取一个组的所有权限列表
@register.filter
def group_permissions(group):
    # 取出数据
    data = group.permissions.all().values_list('codename', flat=True)
    data = list(data)

    return str(data)


# 将显示为None的数据改为空字符串
@register.filter
def clear_none(data):
    if data is None:
        return ''
    else:
        return data


# 将数字转化为百分数
@register.filter
def percentage(data):
    if data is None:
        return data
    # res = '{}%'.format(data*100)
    res = "%.1f%%" % (data * 100)
    return res


# 返回订单日期到计划交期中间当前时间对应的进度百分比
@register.filter
def progress(order_date, scheduled_delivery):
    # 获取当前日期
    current_date = datetime.date.today()
    # 如果当前时间已经超过计划交期，返回False
    if current_date > scheduled_delivery:
        return False
    # 计算百分数
    return ((current_date - order_date).days / (scheduled_delivery - order_date).days)*100

