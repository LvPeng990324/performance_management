# 计算月度绩效考核结果工具
# 交付率：B/A*100%*C*25%*20%
# 成品率：D/E*100%*C*25%*25%
# 医药费：(1-G/F*100%)*C*25%*15%
# 内控综合成本：(1-I/H*100%)*C*25%*30%
# 现场管理：K/L*100%*C*25%*10%

# A：当月约定订单数（给定，录入）
# B：当月实际交付数（内控指标汇总 完成数）
# C：当月挖掘成本（内控指标汇总 目标成本-万元成本 目标成本 给定 录入）
# D:当月成品率（实际成品率）
# E:历史成品率参考值（表里取，数据模拟）
# F:历史医药费月度参考值（表里取，数据模拟）
# G:当月医药费（内控指标汇总 当月医药费）
# H:万元产值成本均值（表里取，数据模拟）
# I:万元产值成本（内控指标汇总 万元成本）
# K：现场管理对应标准符合数（内控指标汇总 ）
# L：现场管理标准目标数（给定，录入）

# 给定，录入：用户(具有公式编辑权限)提供的常量
# 表里取，数据模拟：数据取自本表，只不过历史数据需要先模拟

from ..models import MonthlySalesData
from ..models import QuarterlySalesData
from ..models import InternalControlIndicators
from ..models import MonthlyPerformance
from ..models import ConstantData


# 获取A值方法
def get_A():
    return ConstantData.objects.first().month_plan_order_number


# 获取B值方法
def get_B():
    pass


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


# 获取L值方法
def get_L():
    pass
