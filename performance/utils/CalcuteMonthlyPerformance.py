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
    a = ConstantData.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().month_plan_order_number
    return a


# 获取B值方法
def get_b(need_year, need_month):
    b = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().finished_number
    return b


# 获取C值方法
def get_c(need_year, need_month):
    target_cost = ConstantData.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().target_cost
    cost_per_wan = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().cost_per_wan
    c = target_cost - cost_per_wan
    return c


# 获取D值方法
def get_d(need_year, need_month):
    d = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().actual_well_done_rate
    return d


# 获取E值方法
def get_e(need_year, need_month, history_time):
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
    return e


# 获取F值方法
def get_f(need_year, need_month, history_time):
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
    return f


# 获取G值方法
def get_g(need_year, need_month):
    g = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().month_medical_expenses
    return g


# 获取H值方法
def get_h(need_year, need_month, history_time):
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
    return h


# 获取I值方法
def get_i(need_year, need_month):
    i = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().cost_per_wan
    return i


# 获取K值方法
def get_k(need_year, need_month):
    k = InternalControlIndicators.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().cost_per_wan
    return k


# 获取L值方法
def get_l(need_year, need_month):
    l = ConstantData.objects.filter(
        date__year=need_year, date__month=need_month
    ).first().field_management_compliance_target_number
    return l


def monthly_get_and_refresh(current_year):
    year = int(current_year)
    success_message = ''
    error_message = ''
    for month in range(1, 13):
        history_year = 3  # 历史年限
        try:
            # 尝试获取数据项
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
        except AttributeError:
            obj = MonthlyPerformance.objects.filter(year=year, month=month)
            if obj:
                MonthlyPerformance.objects.filter(year=year, month=month).delete()
            error_message += '%s ' % month
            continue
        try:
            # 从数据库公式表中取到公式并计算
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
                # print("%s年%s月 更新成功" % (year, month))
            else:
                MonthlyPerformance.objects.create(**new_data)
                # print("%s年%s月 成功存入" % (year, month))
            # 反馈成功信息
            success_message += '%s月' % month
        # 公式出错
        except:
            # 删除所有数据
            MonthlyPerformance.objects.all().delete()
            error_message = '刷新失败！请检查公式！'
            return error_message


    # 无错误信息
    if error_message == '':
        return 'success'
    # 有错误信息
    else:
        # 12个月都出错
        if len(error_message) == 27:
            error_message = '所有月份数据不足！请检查数据来源'
        else:
            error_message += '月份数据不足！其余月份更新成功！'
        return error_message

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
# 公式写死
# delivery_rate = round(B / A * C * 0.25 * 0.20, 2)
# well_done_rate = round(D / E * C * 0.25 * 0.25, 2)
# medical_expenses = round((1 - G / F) * C * 0.25 * 0.15, 2)
# overall_cost = round((1 - I / H) * C * 0.25 * 0.30, 2)
# field_management = round(K / L * C * 0.25 * 0.10, 2)
# print(delivery_rate, well_done_rate, medical_expenses, overall_cost, field_management)
