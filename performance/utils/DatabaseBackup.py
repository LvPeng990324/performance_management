# 数据库备份与还原相关方法

import os
from datetime import datetime
from performance_management import settings
from django.http import FileResponse
from django.utils.http import urlquote
from django.contrib import messages
from .SendEmail import send_backup
from apscheduler.schedulers.background import BackgroundScheduler
from ..models import SystemConfig


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
def backup_database(remark):
    # 传入一个参数，字符串类型，代表当前备份备注
    # 调用后即会在backups目录下备份当前数据库
    # 备份文件为json文件
    # 命名规则为当前时间.json
    # 例：2020年03月02日13时04分_{备注}.json

    # 获取当前时间
    current_time = datetime.now()
    # 生成文件名
    file_name = '{}年{}月{}日{}时{}分_{}.json'.format(
        current_time.year,
        current_time.month,
        current_time.day,
        current_time.hour,
        current_time.minute,
        remark,
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


# 恢复数据库
def load_database(file_name):
    # 传入一个文件名，将加载此文件内容到数据库
    # 返回值为Boolean标记是否成功
    # 获取备份文件路径
    file_path = os.path.join(settings.BACKUP_DIR, file_name)
    # 生成恢复命令
    command = 'python manage.py loaddata {}'.format(file_path)
    # 执行命令，获取返回值
    res = os.system(command)
    # 判断返回值
    # 无错误是0，其他值是出错
    if res == 0:
        return True
    else:
        return False


# 删除数据库备份文件
def delete_backup(file_name):
    # 传入一个文件名，将删除此文件
    # 返回值为Boolean标记是否成功
    # 获取要删除的文件路径
    file_path = os.path.join(settings.BACKUP_DIR, file_name)
    # 删除这个文件
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False
    return True


# 下载数据库备份文件
def download_backup(file_name):
    # 传入一个文件名，将下载此文件
    # 返回值为带有文件的response或False
    # 获取要下载的文件路径
    file_path = os.path.join(settings.BACKUP_DIR, file_name)
    try:
        # 读取文件并写入response
        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{}".format(urlquote(file_name))
        return response
    except:
        return False


# 上传数据库备份文件
def upload_backup(request, file):
    # 传入request和一个json文件对象，将把它存入备份文件目录下
    # 返回值为Boolean类型，标记是否成功
    # 判断是否为json文件
    if file.name.split('.')[-1] != 'json':
        # 写入只支持json文件错误提示
        messages.error(request, '仅支持json文件')
        return False
    # 将文件保存到服务器
    try:
        # 获取备份文件目录
        file_path = os.path.join(settings.BACKUP_DIR, file.name)
        # 打开文件进行写操作
        destination = open(file_path, 'wb+')
        # 分块写入文件
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        return True
    except:
        messages.error(request, '保存失败，检查文件名是否有特殊字符并重试')
        return False


# 自动备份数据库调用方法
def auto_backup():
    # 不需要参数
    # 被计划服务调用，用于定期备份并发送邮件
    # 先进行备份
    # 获取当前时间
    current_time = datetime.now()
    # 生成文件名
    remark = '系统自动备份'
    file_name = '{}年{}月{}日{}时{}分_{}.json'.format(
        current_time.year,
        current_time.month,
        current_time.day,
        current_time.hour,
        current_time.minute,
        remark,
    )
    # 获取存储路径
    file_path = os.path.join(settings.BACKUP_DIR, file_name)
    # 生成备份命令
    command = 'python manage.py dumpdata --format=json > {}'.format(file_path)
    # 执行命令，获取返回值
    res = os.system(command)
    # 判断是否备份成功
    # 成功就发送邮件
    # 失败就pass
    if res == 0:
        send_backup(file_path)
    else:
        pass


# 更新自动备份方法
def set_auto_backup():
    # 不需要参数
    # 从数据库中读取天数间隔
    days = SystemConfig.objects.first().days_to_auto_backup
    job = BackgroundScheduler()
    # 清空当前的任务
    if job.get_jobs():
        job.remove_all_jobs()
    # 如果天数间隔小于等于0，则不创建新任务，直接退出
    if days <= 0:
        return
    # 创建任务
    job.add_job(auto_backup, 'interval', days=days, id='auto_backup')
    # 开启当前任务
    job.start()
