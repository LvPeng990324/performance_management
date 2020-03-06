# 专门用来做各种表单的数据项验证


# 公式验证
def cleaned_formula(data):
    # 只允许出现以下字符
    # 1234567890+-*/().ABCDEFGHIKL
    valided_data = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                    '+', '-', '*', '/', '(', ')', '.',
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',)
    # 先对公式取set去重再遍历验证是否存在非法字符
    row_data = set(data)
    for temp in row_data:
        if temp not in valided_data:
            # 存在非法字符，验证失败
            return False
    # 验证完毕，返回公式
    return data


# 数据表单验证
def check_data_format(data, data_format):
    # 传入两个参数
    # data：要验证的数据
    # data_format：数据的期望格式，字符串形式，可以是int、float、str、percentage
    # 返回值为原数据或False，标记是否符合验证结果
    if data_format == 'int':
        try:
            return int(data)
        except:
            return False
    elif data_format == 'float':
        try:
            return float(data)
        except:
            return False
    elif data_format == 'str':
        pass
    elif data_format == 'percentage':
        # 检查最后是不是百分号
        # 是的话就去掉百分号并转浮点数后除以100返回
        # 没有的话就转浮点数返回
        try:
            if data[-1] == '%':
                return float(data[:-1]) / 100
            else:
                return float(data)
        except:
            return False
    else:
        raise Exception('不支持的数据验证类型')
