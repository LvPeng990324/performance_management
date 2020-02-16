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
