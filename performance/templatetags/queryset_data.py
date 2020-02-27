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
    if data is '':
        return data
    # res = '{}%'.format(data*100)
    res = "%.1f%%" % (data * 100)
    return res


# 返回订单日期到计划交期中间当前时间对应的进度百分比
@register.filter
def progress(order_date, scheduled_delivery):
    # 获取当前日期
    current_date = datetime.date.today()
    # 如果当前时间已经超过计划交期，返回-1
    if current_date > scheduled_delivery:
        return -1
    # 如果订单时间跟计划交期在同一天，返回100%
    if order_date == scheduled_delivery:
        return 100
    # 计算百分数
    return ((current_date - order_date).days / (scheduled_delivery - order_date).days)*100


# 返回订单状态
@register.filter
def order_status(order):
    # 设定快到交期阈值
    threshold = 70
    # 获取今天
    current_date = datetime.date.today()
    # 分类数据
    finished_number = order.finished_number
    progress_number = progress(order.order_date, order.scheduled_delivery)
    # 先分是否完成
    if finished_number is None:
        # 未完成订单
        # 判断是否是还未开始的订单
        if current_date < order.order_date:
            # 还未开始
            return '还未开始'
        # 先判断是否是已经逾期
        if progress_number == -1:
            # 已经逾期
            return '已经逾期'
        else:
            # 再根据时间进度是否超过阈值分
            if progress_number <= threshold:
                # 尚未完成
                return '尚未完成'
            else:
                # 快到交期
                return '快到交期'
    else:
        # 已完成订单
        # 再根据finished_number来判断是否逾期完成
        if finished_number == 1:
            # 按时完成
            return '按时完成'
        else:
            # 逾期完成
            return '逾期完成'

