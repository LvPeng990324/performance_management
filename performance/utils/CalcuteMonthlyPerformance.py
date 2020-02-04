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
# from performance import models
import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from datetime import datetime
from performance.models import ConstantData
from performance.models import InternalControlIndicators
from performance.models import MonthlyPerformance


# 获取A值方法
def get_a(need_date):
    try:
        a = ConstantData.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().month_plan_order_number
    except:
        a = '异常'
    return a


# 获取B值方法
def get_b(need_date):
    try:
        b = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().finished_number
    except:
        b = '异常'
    return b


# 获取C值方法
def get_c(need_date):
    try:
        target_cost = ConstantData.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().target_cost
        cost_per_wan = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().cost_per_wan
        c = target_cost - cost_per_wan
    except:
        c = '异常'
    return c


# 获取D值方法
def get_d(need_date):
    try:
        d = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().actual_well_done_rate
    except:
        d = '异常'
    return d


# 获取E值方法
def get_e(need_date):
    # 数据源暂时不明
    try:
        history_well_done_rate_reference = 70
        e = history_well_done_rate_reference
    except:
        e = '异常'
    return e


# 获取F值方法
def get_f(need_date):
    # 数据源暂时不明
    try:
        history_medical_expenses_reference = 3333
        f = history_medical_expenses_reference
    except:
        f = '异常'
    return f


# 获取G值方法
def get_g(need_date):
    try:
        g = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().month_medical_expenses
    except:
        g = '异常'
    return g


# 获取H值方法
def get_h(need_date):
    # 数据源暂时不明
    try:
        cost_per_wan_avg = 666
        h = cost_per_wan_avg
    except:
        h = '异常'
    return h


# 获取I值方法
def get_i(need_date):
    try:
        i = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().cost_per_wan
    except:
        i = '异常'
    return i


# 获取K值方法
def get_k(need_date):
    try:
        k = InternalControlIndicators.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().cost_per_wan
    except:
        k = '异常'
    return k


# 获取L值方法
def get_l(need_date):
    try:
        l = ConstantData.objects.filter(
            date__year=need_date.year, date__month=need_date.month
        ).first().field_management_compliance_target_number
    except:
        l = '异常'
    return l


#
date = '2020-1'  # 查询月份
need_type = '%Y-%m'
date = datetime.strptime(date, need_type)

A = get_a(date)
print('A=', A)
B = get_b(date)
print('B=', B)
C = get_c(date)
print('C=', C)
D = get_d(date)
print('D=', D)
E = get_e(date)
print('E=', E)
F = get_f(date)
print('F=', F)
G = get_g(date)
print('G=', G)
H = get_h(date)
print('H=', H)
I = get_i(date)
print('I=', I)
K = get_k(date)
print('K=', K)
L = get_l(date)
print('L=', L)

delivery_rate = round(B / A * C * 0.25 * 0.20, 2)
well_done_rate = round(D / E * C * 0.25 * 0.25, 2)
medical_expenses = round((1 - G / F) * C * 0.25 * 0.15, 2)
overall_cost = round((1 - I / H) * C * 0.25 * 0.30, 2)
field_management = round(K / L * C * 0.25 * 0.10, 2)


print(delivery_rate, well_done_rate, medical_expenses, overall_cost, field_management)


# delivery_rate = B / A * C * 0.25 * 0.20
# well_done_rate = D / E * C * 0.25 * 0.25
# medical_expenses = (1 - G / F) * C * 0.25 * 0.15
# overall_cost = (1 - I / H) * C * 0.25 * 0.30
# field_management = K / L * C * 0.25 * 0.10
# 交付率：B/A*100%*C*25%*20%
# 成品率：D/E*100%*C*25%*25%
# 医药费：(1-G/F*100%)*C*25%*15%
# 内控综合成本：(1-I/H*100%)*C*25%*30%
# 现场管理：K/L*100%*C*25%*10%
# delivery_rate = models.FloatField(verbose_name='交付率')
# well_done_rate = models.FloatField(verbose_name='成品率')
# medical_expenses = models.FloatField(verbose_name='医药费')
# overall_cost = models.FloatField(verbose_name='内控综合成本')
# field_management = models.FloatField(verbose_name='现场管理')

obj = MonthlyPerformance.objects.filter(date=date)
if obj:
    print("该月数据已存在，无法增添")
else:
    MonthlyPerformance.objects.create(
        date=date,
        delivery_rate=delivery_rate,
        well_done_rate=well_done_rate,
        medical_expenses=medical_expenses,
        overall_cost=overall_cost,
        field_management=field_management,
    )