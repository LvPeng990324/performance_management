# 专门用来做各种表单的数据项验证


# 公式验证
def cleaned_formula(data):
    # 只允许出现以下字符
    # 1234567890+-*/()ABCDEFGHIKL
    valided_data = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '+', '-', '*', '/', '(', ')', 'A', 'B', 'C', 'D',
                    'E', 'F', 'G', 'H', 'I', 'K', 'L', )
    # 先对公式取set去重再遍历验证是否存在非法字符
    row_data = set(data)
    for temp in row_data:
        if temp not in valided_data:
            # 存在非法字符，验证失败
            return False
    # 验证完毕，返回公式
    return data
