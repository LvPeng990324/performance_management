# 发送邮件相关方法
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from ..models import SystemConfig


# 发送带有数据库备份文件的email方法
def send_backup(file_path):
    # 一个参数，要发送的备份文件路径
    # 从配置文件读取发送邮箱
    from_email = settings.EMAIL_HOST_USER
    # 邮件标题
    subject = '利润绩效系统系统自动备份'
    # 邮件正文
    context = '这是系统自动发送的邮件，请勿回复，附件是数据库定时备份的文件'
    # 从数据库中取得要发送的email
    to_email = SystemConfig.objects.first().backup_to_email
    # 创建邮件对象
    msg = EmailMultiAlternatives(subject, context, from_email, [to_email])
    # 附加附件
    msg.attach_file(file_path)
    # 发送邮件
    msg.send()


# 发送邮箱验证方法
def send_verification_code(to_email, verification_code):
    # 两个参数，要发送的邮箱地址以及验证码
    # 从配置文件读取发送邮箱
    from_email = settings.EMAIL_HOST_USER
    # 邮件标题
    subject = '利润绩效系统验证码'
    # 邮件正文
    context = '欢迎使用绩效管理系统，你的验证码为{}，请不要回复此邮件。'.format(verification_code)
    # 从数据库中取得要发送的email
    to_email = SystemConfig.objects.first().backup_to_email
    # 创建邮件对象
    msg = EmailMultiAlternatives(subject, context, from_email, [to_email])
    # 发送邮件
    msg.send()
