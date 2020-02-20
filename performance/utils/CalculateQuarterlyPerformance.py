import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from performance.models import QuarterlySalesData
from performance.models import QuarterlyPerformance
from performance.models import QuarterlyFormula


# 获取季度营业额
def get_a(need_year, need_quarter):
    a = QuarterlySalesData.objects.get(
        year=need_year, quarter=need_quarter).turnover
    return a


# 获取营业费用
def get_b(need_year, need_quarter):
    b = QuarterlySalesData.objects.get(
        year=need_year, quarter=need_quarter).operating_expenses
    return b


# 获取回款额
def get_c(need_year, need_quarter):
    c = QuarterlySalesData.objects.get(
        year=need_year, quarter=need_quarter).amount_repaid
    return c


# 获取库存量
def get_d(need_year, need_quarter):
    d = QuarterlySalesData.objects.get(
        year=need_year, quarter=need_quarter).inventory
    return d


# 获取利润额
def get_e(need_year, need_quarter):
    e = QuarterlySalesData.objects.get(
        year=need_year, quarter=need_quarter).profit
    return e


def quarterly_get_and_refresh(current_year):
    year = int(current_year)
    success_message = ''
    error_message = ''
    for quarter in range(1, 5):
        try:
            # 尝试获取数据项
            A = get_a(year, quarter)
            B = get_b(year, quarter)
            C = get_c(year, quarter)
            D = get_d(year, quarter)
            E = get_e(year, quarter)
            print(A,B,C,D,E)
        except AttributeError:
            obj = QuarterlyPerformance.objects.filter(year=year, quarter=quarter)
            if obj:
                QuarterlyPerformance.objects.filter(year=year, quarter=quarter).delete()
            error_message += '%s ' % quarter
            continue
        try:
            # 从数据库公式表中取到公式并计算
            turnover = round(eval(QuarterlyFormula.objects.filter(
                target_item='营业额').first().formula), 2)
            operating_rate = round(eval(QuarterlyFormula.objects.filter(
                target_item='营业费率').first().formula), 2)
            repaid_rate = round(eval(QuarterlyFormula.objects.filter(
                target_item='回款率').first().formula), 2)
            inventory_rate = round(eval(QuarterlyFormula.objects.filter(
                target_item='库存率').first().formula), 2)
            profit_rate = round(eval(QuarterlyFormula.objects.filter(
                target_item='利润率').first().formula), 2)
            # print(turnover, operating_rate, repaid_rate, inventory_rate, profit_rate)

            new_data = {
                'year': year,
                'quarter': quarter,
                'turnover': turnover,
                'operating_rate': operating_rate,
                'repaid_rate': repaid_rate,
                'inventory_rate': inventory_rate,
                'profit_rate': profit_rate,
            }

            obj = QuarterlyPerformance.objects.filter(year=year, quarter=quarter)
            if obj:
                # 如果该月数据已存在，则更新
                QuarterlyPerformance.objects.filter(year=year, quarter=quarter).update(**new_data)
                # print("%s年%s季度 更新成功" % (year, quarter))
            else:
                QuarterlyPerformance.objects.create(**new_data)
                # print("%s年%s季度 成功存入" % (year, quarter))
            success_message += '%s ' % quarter
        # 公式出错
        except:
            # 删除所有数据
            QuarterlyPerformance.objects.all().delete()
            error_message = '刷新失败！请检查公式！'
            return error_message

    # 无错误信息
    if error_message == '':
        return 'success'
    # 有错误信息
    else:
        # 四季度都出错
        if len(error_message) == 8:
            error_message = '所有季度数据不足！请检查数据来源'
        else:
            error_message += '季度数据不足！其余季度更新成功！'
        return error_message
