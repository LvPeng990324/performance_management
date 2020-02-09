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
import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from django.db.models import Count, Sum, Avg
from performance.models import ConstantData
from performance.models import QuarterlySalesData
from performance.models import QuarterlyPerformance


# 获取A值方法
def get_a(need_year):
    try:
        a = ConstantData.objects.filter(date__year=need_year).first().annual_target_turnover
    except:
        a = '异常'
    return a


# 获取B值方法
def get_b(need_year):
    try:
        b = ConstantData.objects.filter(date__year=need_year).first().annual_target_award
    except:
        b = '异常'
    return b


# 获取C值方法
def get_c(need_year, need_quarter):
    try:
        c = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().turnover
    except:
        c = '异常'
    return c


# 获取D值方法
def get_d(need_year, need_quarter):
    try:
        turnover = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().turnover
        operating_expenses = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().operating_expenses
        d = operating_expenses / turnover
    except:
        d = '异常'
    return d


# 获取E值方法
def get_e(need_year, need_quarter, history_time):
    try:
        start_year = need_year - history_time
        start_quarter = need_quarter
        # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
        # 1.获取2016年6月及以上月份的数据
        data1 = QuarterlySalesData.objects.filter(
            year=start_year, quarter__gte=start_quarter)
        # 2.获取2017、2018年的数据
        data2 = QuarterlySalesData.objects.filter(
            year__gt=start_year, year__lt=need_year)
        # 3.获取2019年5月及以下月份的数据
        data3 = QuarterlySalesData.objects.filter(
            year=need_year, quarter__lt=start_quarter)
        data_list = data1 | data2 | data3
        all_operating_rate = 0
        for data in data_list:
            all_operating_rate += data.operating_expenses / data.turnover
        e = all_operating_rate / data_list.count()
    except:
        e = '异常'
    return e


# 获取F值方法
def get_f(need_year, need_quarter):
    try:
        turnover = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().turnover
        amount_repaid = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().amount_repaid
        f = amount_repaid / turnover
    except:
        f = '异常'
    return f


# 获取G值方法
def get_g(need_year, need_quarter):
    try:
        turnover = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().turnover
        inventory = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().inventory
        g = inventory / turnover
    except:
        g = '异常'
    return g


# 获取H值方法
def get_h(need_year, need_quarter, history_time):
    try:
        start_year = need_year - history_time
        start_quarter = need_quarter
        # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
        # 1.获取2016年6月及以上月份的数据
        data1 = QuarterlySalesData.objects.filter(
            year=start_year, quarter__gte=start_quarter)
        # 2.获取2017、2018年的数据
        data2 = QuarterlySalesData.objects.filter(
            year__gt=start_year, year__lt=need_year)
        # 3.获取2019年5月及以下月份的数据
        data3 = QuarterlySalesData.objects.filter(
            year=need_year, quarter__lt=start_quarter)
        data_list = data1 | data2 | data3
        all_inventory_rate = 0
        for data in data_list:
            all_inventory_rate += data.inventory / data.turnover
        h = all_inventory_rate / data_list.count()
    except:
        h = '异常'
    return h


# 获取I值方法
def get_i(need_year, need_quarter):
    try:
        turnover = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().turnover
        profit = QuarterlySalesData.objects.filter(
            year=need_year, quarter=need_quarter).first().profit
        i = profit / turnover
    except:
        i = '异常'
    return i


# 获取K值方法
def get_k(need_year, need_quarter, history_time):
    try:
        start_year = need_year - history_time
        start_quarter = need_quarter
        # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
        # 1.获取2016年6月及以上月份的数据
        data1 = QuarterlySalesData.objects.filter(
            year=start_year, quarter__gte=start_quarter)
        # 2.获取2017、2018年的数据
        data2 = QuarterlySalesData.objects.filter(
            year__gt=start_year, year__lt=need_year)
        # 3.获取2019年5月及以下月份的数据
        data3 = QuarterlySalesData.objects.filter(
            year=need_year, quarter__lt=start_quarter)
        data_list = data1 | data2 | data3
        all_profit_rate = 0
        for data in data_list:
            all_profit_rate += data.profit / data.turnover
        k = all_profit_rate / data_list.count()
    except:
        k = '异常'
    return k


def quarterly_get_and_refresh():
    # 更新2017-2019的数据
    for year in range(2017, 2021):
        for quarter in range(1, 5):
            history_year = 3  # 历史年限
            A = get_a(year)
            B = get_b(year)
            C = get_c(year, quarter)
            D = get_d(year, quarter)
            E = get_e(year, quarter, history_year)
            F = get_f(year, quarter)
            G = get_g(year, quarter)
            H = get_h(year, quarter, history_year)
            I = get_i(year, quarter)
            K = get_k(year, quarter, history_year)
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

            try:
                turnover = round(C * (B / A) * 0.2 / A * 0.25 * C, 2)  # 营业额
                operating_rate = round(C * (B / A) * 0.3 / (1 - E) * (1 - D), 2)  # 营业费率
                repaid_rate = round(C * (B / A) * 0.2 * F, 2)  # 回款率
                inventory_rate = round(C * (B / A) * 0.1 / (1 - H) * (1 - G), 2)  # 库存率
                profit_rate = round(C * (B / A) * 0.2 / K * I, 2)  # 利润率
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
                    print("%s年%s季度 更新成功" % (year, quarter))
                else:
                    QuarterlyPerformance.objects.create(**new_data)
                    print("%s年%s季度 成功存入" % (year, quarter))

            except:
                print("%s年%s季度 数据异常，操作失败" % (year, quarter))
    return 'success'


if __name__ == '__main__':
    quarterly_get_and_refresh()
