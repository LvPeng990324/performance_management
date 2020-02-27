# 交付率：计划交期为当月的订单中按时完成的订单/计划交期为当月的订单*100%（用完成数就能做）
# 成品率：计划交期为当月的订单中当月实际成品率累加/计划交期为当月的订单中订单数*100%
# 医药费：当月完成的订单中当月医药费累加-当月完成的订单中当月实际医药费累加
# 内控综合成本（改成当月挖掘成本）：当月完成的订单中目标成本-当月完成的订单中实际成本
# 现场管理（改成现场管理符合率）：当月完成的订单中实际符合/当月完成的订单中目标符合*100%


import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, Avg
from performance.models import InternalControlIndicators
from performance.models import MonthlyPerformance
from performance.models import MonthlyFormula


# 获取当月完成订单数
def get_a(need_year, need_month):
    a = InternalControlIndicators.objects.filter(
        scheduled_delivery__year=need_year,
        scheduled_delivery__month=need_month,
        finished_number=1,
    ).count()
    # print(a)
    return a


# 获取当月计划订单数
def get_b(need_year, need_month):
    b = InternalControlIndicators.objects.filter(
        scheduled_delivery__year=need_year,
        scheduled_delivery__month=need_month,
    ).count()
    # print(b)
    return b


# 获取当月实际成品率累加
def get_c(need_year, need_month):
    c = InternalControlIndicators.objects.filter(
        scheduled_delivery__year=need_year,
        scheduled_delivery__month=need_month,
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_actual_well_done_rate=Sum('actual_well_done_rate'))
    c = c['sum_actual_well_done_rate']
    if c is None:
        c = 0
    # print(c)
    return c


# 获取当月计划医药费
def get_d(need_year, need_month):
    d = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_target_medical_expenses=Sum('target_medical_expenses'))
    d = d['sum_target_medical_expenses']
    # print(d)
    return d


# 获取当月实际医药费
def get_e(need_year, need_month):
    e = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_actual_medical_expenses=Sum('actual_medical_expenses'))
    e = e['sum_actual_medical_expenses']
    # print(e)
    return e


# 获取订单目标成本
def get_f(need_year, need_month):
    f = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_target_comprehensive_cost=Sum('target_comprehensive_cost'))
    f = f['sum_target_comprehensive_cost']
    # print(f)
    return f


# 获取订单实际成本
def get_g(need_year, need_month):
    g = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_actual_cost=Sum('actual_cost'))
    g = g['sum_actual_cost']
    # print(g)
    return g


# 获取订单实际符合
def get_h(need_year, need_month):
    h = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_actual_management_compliance=Sum('actual_management_compliance'))
    h = h['sum_actual_management_compliance']
    # print(h)
    return h


# 获取目标符合
def get_i(need_year, need_month):
    i = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_target_management_compliance=Sum('target_management_compliance'))
    i = i['sum_target_management_compliance']
    # print(i)
    return i


def monthly_get_and_refresh(year_list=InternalControlIndicators.objects.values_list('actual_delivery__year', flat=True).distinct()):
    # print(year_list)
    for year in year_list:
        success_message = ''
        error_message = ''
        # 排除内控数据不完整的情况
        if year is None:
            continue
        for month in range(1, 13):
            try:
                # 尝试获取数据项
                A = get_a(year, month)
                B = get_b(year, month)
                C = get_c(year, month)
                D = get_d(year, month)
                E = get_e(year, month)
                F = get_f(year, month)
                G = get_g(year, month)
                H = get_h(year, month)
                I = get_i(year, month)
                if A is None or B is None or C is None or D is None or E is None or F is None or G is None or H is None or I is None:
                    obj = MonthlyPerformance.objects.filter(year=year, month=month)
                    if obj:
                        MonthlyPerformance.objects.filter(year=year, month=month).delete()
                    error_message += '%s ' % month
                    continue
                # print('A=', A)
                # print('B=', B)
                # print('C=', C)
                # print('D=', D)
                # print('E=', E)
                # print('F=', F)
                # print('G=', G)
                # print('H=', H)
                # print('I=', I)
            except AttributeError:
                obj = MonthlyPerformance.objects.filter(year=year, month=month)
                if obj:
                    MonthlyPerformance.objects.filter(year=year, month=month).delete()
                error_message += '%s ' % month
                continue
            # 从数据库公式表中取到公式并计算
            try:
                # 避免除0储错误
                if B == 0:
                    delivery_rate = 0
                    well_done_rate = 0
                else:
                    delivery_rate = round(eval(MonthlyFormula.objects.filter(
                        target_item='交付率').first().formula), 3)
                    well_done_rate = round(eval(MonthlyFormula.objects.filter(
                        target_item='成品率').first().formula), 3)
                medical_expenses = round(eval(MonthlyFormula.objects.filter(
                    target_item='医药费').first().formula), 3)
                month_dig_cost = round(eval(MonthlyFormula.objects.filter(
                    target_item='当月挖掘成本').first().formula), 3)
                field_management_well_rate = round(eval(MonthlyFormula.objects.filter(
                    target_item='现场管理符合率').first().formula), 3)
                # print(delivery_rate, well_done_rate, medical_expenses, month_dig_cost, field_management_well_rate)

                new_data = {
                    'year': year,
                    'month': month,
                    'delivery_rate': delivery_rate,
                    'well_done_rate': well_done_rate,
                    'medical_expenses': medical_expenses,
                    'month_dig_cost': month_dig_cost,
                    'field_management_well_rate': field_management_well_rate,
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
                MonthlyPerformance.objects.filter(year=year).delete()
                error_message = '刷新失败！请检查公式！'
                # return error_message
                continue

        # 无错误信息
        # if error_message == '':
            # return 'success'
        # 有错误信息
        # else:
            # 12个月都出错
            # if len(error_message) == 27:
            #     error_message = '所有月份数据不足！请检查数据来源'
            # else:
            #     error_message += '月份数据不足！其余月份更新成功！'
            # return error_message
