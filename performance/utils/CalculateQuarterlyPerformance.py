# 计算季度绩效考核结果工具
# 营业额：C*(B/A)%*20%/A*25%*C
# 营业费率：C*(B/A)%*30%/(1-E)*(1-D)
# 回款率：C*(B/A)%*20%/100%*F
# 库存率：C*(B/A)%*10%/(1-H)*(1-G)
# 利润率：C*(B/A)%*20%/K*Y

# A：年度目标营业额（提前给定，录入）
# B：年度目标奖金额（提前给定，录入）
# C：季度实际营业额（表里取、数据模拟）
# D:季度实际营业费率（营业费用/营业额）
# E:前三年营业费率参考值（表里取、数据模拟）
# F:季度实际回款率（回款额/营业额）
# G:季度实际库存率（库存量/营业额）
# H:前三年库存率参考值（表里取、数据模拟）
# I:季度实际利润率（利润额/营业额）
# K：前三年利润率参考值（表里取、数据模拟）

from ..models import MonthlySalesData
from ..models import QuarterlySalesData
from ..models import InternalControlIndicators
from ..models import QuarterlyPerformance
from ..models import ConstantData


# 获取A值方法
def get_A():
    return ConstantData.objects.first().annual_target_turnover


# 获取B值方法
def get_B():
    return ConstantData.objects.first().annual_target_award


# 获取C值方法
def get_C():
    pass


# 获取D值方法
def get_D():
    pass


# 获取E值方法
def get_E():
    pass


# 获取F值方法
def get_F():
    pass


# 获取G值方法
def get_G():
    pass


# 获取H值方法
def get_H():
    pass


# 获取I值方法
def get_I():
    pass


# 获取K值方法
def get_K():
    pass
