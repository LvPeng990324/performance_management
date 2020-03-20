# 发送短信相关方法
import urllib
import urllib.request
import hashlib
from django.conf import settings


def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


def send_verification_code(phone, verification_code):
    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
        '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词'
    }

    smsapi = settings.SMSAPI
    # 短信平台账号
    user = settings.SMSUSER
    # 短信平台密码
    password = md5(settings.SMSPASSWORD)
    # 要发送的短信内容
    content = '您的验证码为{}，仅本次会话有效，请尽快填写'.format(verification_code)
    # 要发送短信的手机号码
    phone = phone

    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    the_page = response.read().decode('utf-8')
    return statusStr[the_page]