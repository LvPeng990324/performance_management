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
from performance.models import QuarterlyFormula
from performance.models import QuarterlyAwardFormula
from performance.models import QuarterlyAward


# 获取A值方法
def get_a():
    a = ConstantData.objects.last().annual_target_turnover
    return a


# 获取B值方法
def get_b():
    b = ConstantData.objects.last().annual_target_award
    return b


# 获取C值方法
def get_c(need_year, need_quarter):
    c = QuarterlyPerformance.objects.filter(
        year=need_year, quarter=need_quarter).first().turnover
    return c


# 获取D值方法
def get_d(need_year, need_quarter):
    d = QuarterlyPerformance.objects.filter(
        year=need_year, quarter=need_quarter).first().operating_rate
    return d


# 获取E值方法
def get_e(need_year, need_quarter, history_time):
    start_year = need_year - history_time
    start_quarter = need_quarter
    # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
    # 1.获取2016年2季度及以后的数据
    data1 = QuarterlyPerformance.objects.filter(
        year=start_year, quarter__gte=start_quarter)
    # 2.获取2017、2018年的数据
    data2 = QuarterlyPerformance.objects.filter(
        year__gt=start_year, year__lt=need_year)
    # 3.获取2019年2季度之前的数据
    data3 = QuarterlyPerformance.objects.filter(
        year=need_year, quarter__lt=start_quarter)
    data_list = data1 | data2 | data3
    if data_list.count() == 12:
        e = data_list.aggregate(avg_operating_rate=Avg('operating_rate'))['avg_operating_rate']
    else:
        e = None
    return e


# 获取F值方法
def get_f(need_year, need_quarter):
    f = QuarterlyPerformance.objects.filter(
        year=need_year, quarter=need_quarter).first().repaid_rate
    return f


# 获取G值方法
def get_g(need_year, need_quarter):
    g = QuarterlyPerformance.objects.filter(
        year=need_year, quarter=need_quarter).first().inventory_rate
    return g


# 获取H值方法
def get_h(need_year, need_quarter, history_time):
    start_year = need_year - history_time
    start_quarter = need_quarter
    # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
    # 1.获取2016年2季度及以后的数据
    data1 = QuarterlyPerformance.objects.filter(
        year=start_year, quarter__gte=start_quarter)
    # 2.获取2017、2018年的数据
    data2 = QuarterlyPerformance.objects.filter(
        year__gt=start_year, year__lt=need_year)
    # 3.获取2019年2季度之前的数据
    data3 = QuarterlyPerformance.objects.filter(
        year=need_year, quarter__lt=start_quarter)
    data_list = data1 | data2 | data3
    if data_list.count() == 12:
        h = data_list.aggregate(avg_inventory_rate=Avg('inventory_rate'))['avg_inventory_rate']
    else:
        h = None
    return h


# 获取I值方法
def get_i(need_year, need_quarter):
    i = QuarterlyPerformance.objects.filter(
        year=need_year, quarter=need_quarter).first().profit_rate
    return i


# 获取K值方法
def get_k(need_year, need_quarter, history_time):
    start_year = need_year - history_time
    start_quarter = need_quarter
    # 例：现need_year为2019，need_quarter为2，则需获取2016.2季度.-2019.1季度的数据
    # 1.获取2016年2季度及以后的数据
    data1 = QuarterlyPerformance.objects.filter(
        year=start_year, quarter__gte=start_quarter)
    # 2.获取2017、2018年的数据
    data2 = QuarterlyPerformance.objects.filter(
        year__gt=start_year, year__lt=need_year)
    # 3.获取2019年2季度之前的数据
    data3 = QuarterlyPerformance.objects.filter(
        year=need_year, quarter__lt=start_quarter)
    data_list = data1 | data2 | data3
    if data_list.count() == 12:
        k = data_list.aggregate(avg_profit_rate=Avg('profit_rate'))['avg_profit_rate']
    else:
        k = None
    return k


def quarterly_get_and_refresh(year_list=QuarterlyPerformance.objects.order_by('year').values_list('year', flat=True).distinct()):
    # 每次都需从小到大刷新所有年份
    print(year_list)
    for year in year_list:
        print(year)
        success_message = ''
        error_message = ''
        history_year = 3  # 历史年限
        # 排除内控数据不完整的情况
        if year is None:
            continue
        for quarter in range(1, 5):
            try:
                # 尝试获取数据项
                A = get_a()
                B = get_b()
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
            except:
                obj = QuarterlyAward.objects.filter(year=year, quarter=quarter)
                if obj:
                    QuarterlyAward.objects.filter(year=year, quarter=quarter).delete()
                error_message += '%s ' % quarter
                continue
            try:
                # 从数据库公式表中取到公式并计算
                turnover_award = round(eval(QuarterlyAwardFormula.objects.filter(
                    target_item='营业额').first().formula), 2)
                operating_rate_award = round(eval(QuarterlyAwardFormula.objects.filter(
                    target_item='营业费率').first().formula), 2)
                repaid_rate_award = round(eval(QuarterlyAwardFormula.objects.filter(
                    target_item='回款率').first().formula), 2)
                inventory_rate_award = round(eval(QuarterlyAwardFormula.objects.filter(
                    target_item='库存率').first().formula), 2)
                profit_rate_award = round(eval(QuarterlyAwardFormula.objects.filter(
                    target_item='利润率').first().formula), 2)
                total = round(turnover_award + turnover_award + repaid_rate_award + inventory_rate_award + profit_rate_award,2)
                print(turnover_award, operating_rate_award, repaid_rate_award, inventory_rate_award, profit_rate_award)

                new_data = {
                    'year': year,
                    'quarter': quarter,
                    'turnover_award': turnover_award,
                    'operating_rate_award': turnover_award,
                    'repaid_rate_award': repaid_rate_award,
                    'inventory_rate_award': inventory_rate_award,
                    'profit_rate_award': profit_rate_award,
                    'total': total
                }

                obj = QuarterlyAward.objects.filter(year=year, quarter=quarter)
                if obj:
                    # 如果该月数据已存在，则更新
                    QuarterlyAward.objects.filter(year=year, quarter=quarter).update(**new_data)
                    print("%s年%s季度 更新成功" % (year, quarter))
                else:
                    QuarterlyAward.objects.create(**new_data)
                    print("%s年%s季度 成功存入" % (year, quarter))
                success_message += '%s ' % quarter
            # 公式出错
            except:
                # 删除所有数据
                QuarterlyAward.objects.all().delete()
                # error_message = '刷新失败！请检查公式！'
                # return error_message
                continue
        #
        # # 无错误信息
        # if error_message == '':
        #     return 'success'
        # # 有错误信息
        # else:
        #     # 四季度都出错
        #     if len(error_message) == 8:
        #         error_message = '所有季度数据不足！请检查数据来源'
        #     else:
        #         error_message += '季度数据不足！其余季度更新成功！'
        #     return error_message


if __name__ == '__main__':
    quarterly_get_and_refresh()

# 公式写死
# turnover = round(C * (B / A) * 0.2 / A * 0.25 * C, 2)  # 营业额
# operating_rate = round(C * (B / A) * 0.3 / (1 - E) * (1 - D), 2)  # 营业费率
# repaid_rate = round(C * (B / A) * 0.2 * F, 2)  # 回款率
# inventory_rate = round(C * (B / A) * 0.1 / (1 - H) * (1 - G), 2)  # 库存率
# profit_rate = round(C * (B / A) * 0.2 / K * I, 2)  # 利润率
# print(turnover, operating_rate, repaid_rate, inventory_rate, profit_rate)
