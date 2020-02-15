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

import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, Avg
from performance.models import ConstantData
from performance.models import InternalControlIndicators
from performance.models import MonthlyPerformance
from performance.models import MonthlyFormula


# 获取A值方法
def get_a(need_year, need_month):
    try:
        a = ConstantData.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().month_plan_order_number
    except:
        a = '异常'
    return a


# 获取B值方法
def get_b(need_year, need_month):
    try:
        b = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().finished_number
    except:
        b = '异常'
    return b


# 获取C值方法
def get_c(need_year, need_month):
    try:
        target_cost = ConstantData.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().target_cost
        cost_per_wan = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().cost_per_wan
        c = target_cost - cost_per_wan
    except:
        c = '异常'
    return c


# 获取D值方法
def get_d(need_year, need_month):
    try:
        d = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().actual_well_done_rate
    except:
        d = '异常'
    return d


# 获取E值方法
def get_e(need_year, need_month, history_time):
    try:
        start_year = need_year - history_time
        start_month = need_month
        # 例：现need_year为2019，need_month为6，则需获取2016.6-2019.5的数据
        # 1.获取2016年6月后的数据
        e1 = InternalControlIndicators.objects.filter(
            date__year=start_year, date__month__gt=start_month)
        # 2.获取2017、2018年的数据
        e2 = InternalControlIndicators.objects.filter(
            date__year__gt=start_year, date__year__lt=need_year)
        # 3.获取2019年5月及以前的数据
        e3 = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month__lte=start_month)
        e = e1 | e2 | e3
        e = e.aggregate(history_avg=Avg('actual_well_done_rate'))['history_avg']
    except:
        e = '异常'
    return e


# 获取F值方法
def get_f(need_year, need_month, history_time):
    try:
        start_year = need_year - history_time
        start_month = need_month
        # 例：现need_year为2019，need_month为6，则需获取2016.6-2019.5的数据
        # 1.获取2016年6月后的数据
        f1 = InternalControlIndicators.objects.filter(
            date__year=start_year, date__month__gt=start_month)
        # 2.获取2017、2018年的数据
        f2 = InternalControlIndicators.objects.filter(
            date__year__gt=start_year, date__year__lt=need_year)
        # 3.获取2019年及以前的数据
        f3 = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month__lte=start_month)
        f = f1 | f2 | f3
        f = f.aggregate(history_avg=Avg('month_medical_expenses'))['history_avg']
    except:
        f = '异常'
    return f


# 获取G值方法
def get_g(need_year, need_month):
    try:
        g = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().month_medical_expenses
    except:
        g = '异常'
    return g


# 获取H值方法
def get_h(need_year, need_month, history_time):
    try:
        start_year = need_year - history_time
        start_month = need_month
        # 例：现need_year为2019，need_month为6，则需获取2016.6-2019.5的数据
        # start_year=2016
        # start_month=6
        # 1.获取2016年6月后的数据
        h1 = InternalControlIndicators.objects.filter(
            date__year=start_year, date__month__gt=start_month)
        # 2.获取2017、2018年的数据
        h2 = InternalControlIndicators.objects.filter(
            date__year__gt=start_year, date__year__lt=need_year)
        # 3.获取2019年6月及以前的数据
        h3 = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month__lte=start_month)
        h = h1 | h2 | h3
        h = h.aggregate(history_avg=Avg('cost_per_wan'))['history_avg']
    except:
        h = '异常'
    return h


# 获取I值方法
def get_i(need_year, need_month):
    try:
        i = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().cost_per_wan
    except:
        i = '异常'
    return i


# 获取K值方法
def get_k(need_year, need_month):
    try:
        k = InternalControlIndicators.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().cost_per_wan
    except:
        k = '异常'
    return k


# 获取L值方法
def get_l(need_year, need_month):
    try:
        l = ConstantData.objects.filter(
            date__year=need_year, date__month=need_month
        ).first().field_management_compliance_target_number
    except:
        l = '异常'
    return l


def monthly_get_and_refresh(current_year):
    # 更新2017-2019的数据
    error_time = 0
    year = int(current_year)
    for month in range(1, 13):
        history_year = 3  # 历史年限

        A = get_a(year, month)
        B = get_b(year, month)
        C = get_c(year, month)
        D = get_d(year, month)
        E = get_e(year, month, history_year)
        F = get_f(year, month, history_year)
        G = get_g(year, month)
        H = get_h(year, month, history_year)
        I = get_i(year, month)
        K = get_k(year, month)
        L = get_l(year, month)
        # print('A=', A)
        # print('B=', B)
        # print('C=', C)
        # print('D=', D)
        # print('E=', E)
        # print('F=', F)
        # print('G=', G)
        # print('H=', H)
        # print('I=', I)
        # print('K=', K)
        # print('L=', L)

        try:
            # 公式写死
            # delivery_rate = round(B / A * C * 0.25 * 0.20, 2)
            # well_done_rate = round(D / E * C * 0.25 * 0.25, 2)
            # medical_expenses = round((1 - G / F) * C * 0.25 * 0.15, 2)
            # overall_cost = round((1 - I / H) * C * 0.25 * 0.30, 2)
            # field_management = round(K / L * C * 0.25 * 0.10, 2)
            # print(delivery_rate, well_done_rate, medical_expenses, overall_cost, field_management)

            # 从数据库中取到公式
            delivery_rate = round(eval(MonthlyFormula.objects.filter(
                target_item='交付率').first().formula), 2)
            well_done_rate = round(eval(MonthlyFormula.objects.filter(
                target_item='成品率').first().formula), 2)
            medical_expenses = round(eval(MonthlyFormula.objects.filter(
                target_item='医药费').first().formula), 2)
            overall_cost = round(eval(MonthlyFormula.objects.filter(
                target_item='内控综合成本').first().formula), 2)
            field_management = round(eval(MonthlyFormula.objects.filter(
                target_item='现场管理').first().formula), 2)
            # print(delivery_rate, well_done_rate, medical_expenses, overall_cost, field_management)

            new_data = {
                'year': year,
                'month': month,
                'delivery_rate': delivery_rate,
                'well_done_rate': well_done_rate,
                'medical_expenses': medical_expenses,
                'overall_cost': overall_cost,
                'field_management': field_management,
            }

            obj = MonthlyPerformance.objects.filter(year=year, month=month)
            if obj:
                # 如果该月数据已存在，则更新
                MonthlyPerformance.objects.filter(year=year, month=month).update(**new_data)
                print("%s年%s月 更新成功" % (year, month))
            else:
                MonthlyPerformance.objects.create(**new_data)
                print("%s年%s月 成功存入" % (year, month))

        except:
            print("%s年%s月 数据异常，操作失败" % (year, month))

    # 如果12个月都获取失败，则返回错误信息
    if error_time == 12:
        return 'error'

    return 'success'


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
