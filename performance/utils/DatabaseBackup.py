# 数据库备份与还原相关方法

import os
from datetime import datetime
from performance_management import settings


# 读取备份文件方法
def get_backups():
    # 不需要参数，调用后返回backups目录下所有.json文件的文件名中包含的时间信息
    # 获取存储路径
    file_path = settings.BACKUP_DIR
    # 读取目录下内容
    # 去除非json文件
    backups = []
    for temp in os.listdir(file_path):
        if temp.split('.')[-1] == 'json':
            backups.append(temp)
    # 返回备份文件名列表
    return backups


# 备份数据库
def backup_database():
    # 不需要参数，调用后即会在backups目录下备份当前数据库
    # 备份文件为json文件
    # 命名规则为当前时间.json
    # 例：2020年03月02日13时04分.json

    # 获取当前时间
    current_time = datetime.now()
    # 生成文件名
    file_name = '{}年{}月{}日{}时{}分.json'.format(
        current_time.year,
        current_time.month,
        current_time.day,
        current_time.hour,
        current_time.minute,
    )
    # 获取存储路径
    file_path = os.path.join(settings.BACKUP_DIR, file_name)
    # 生成备份命令
    command = 'python manage.py dumpdata --format=json > {}'.format(file_path)
    # 执行命令，获取返回值
    res = os.system(command)
    # 判断返回值
    # 无错误是0，其他值是出错
    if res == 0:
        return True
    else:
        return False

