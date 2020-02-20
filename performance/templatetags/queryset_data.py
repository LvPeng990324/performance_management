# 用于获取queryset数据类型具体数据的过滤器文件
from django.template import Library

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
    if not data:
        return data
    res = '{}%'.format(data*100)
    return res
