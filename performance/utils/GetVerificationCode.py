# 用于生成验证码方法

from random import randint


# 获取六位验证码方法
def get_verification_code():
    return str(randint(100000, 999999))
