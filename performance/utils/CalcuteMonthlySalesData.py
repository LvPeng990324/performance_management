import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, Avg
from performance.models import InternalControlIndicators
from performance.models import MonthlySalesData
from django.db.models import F


# 获取当月总营业额
def get_turnover(need_year, need_month):
    turnover = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_order_money=Sum('order_money'))
    turnover = turnover['sum_order_money']
    if turnover is None:
        turnover = 0
    return turnover


# 获取当月总营业费用
def get_operating_expenses(need_year, need_month):
    operating_expenses = InternalControlIndicators.objects.filter(
        actual_delivery__year=need_year,
        actual_delivery__month=need_month,
    ).aggregate(sum_operating_expenses=Sum('operating_expenses'))
    operating_expenses = operating_expenses['sum_operating_expenses']
    if operating_expenses is None:
        operating_expenses = 0
    return operating_expenses

# 获取当月总回款额
def get_amount_repaid(need_year, need_month):
    amount_repaid = InternalControlIndicators.objects.filter(
        actual_give_money_day__year=need_year,
        actual_give_money_day__month=need_month,
        scheduled_give_money_day__gte=F('actual_give_money_day'),
    ).aggregate(sum_order_money=Sum('order_money'))
    amount_repaid = amount_repaid['sum_order_money']
    if amount_repaid is None:
        amount_repaid = 0
    return amount_repaid

# 获取当月库存量
def get_inventory(need_year, need_month):
    try:
        inventory = MonthlySalesData.objects.filter(
            year=need_year,
            month=need_month,
        ).first().inventory
    except:
        inventory = 0
    return inventory

def monthly_saledata_get_and_refresh(year_list=InternalControlIndicators.objects.values_list('actual_delivery__year', flat=True).distinct()):
    print(year_list)
    for year in year_list:
        # 排除内控数据不完整的情况
        if year is None:
            continue
        for month in range(1, 13):
            try:
                # 尝试获取数据项
                turnover = get_turnover(year, month)
                operating_expenses = get_operating_expenses(year, month)
                amount_repaid = get_amount_repaid(year, month)
                inventory = get_inventory(year, month)
                profit = turnover - operating_expenses
                if turnover == 0 and operating_expenses == 0 and amount_repaid == 0:
                    continue
                # print('turnover=', turnover)
                # print('operating_expenses=', operating_expenses)
                # print('amount_repaid=', amount_repaid)
                # print('inventory=', inventory)
                # print('profit=', profit)
            except:
                obj = MonthlySalesData.objects.filter(year=year, month=month)
                if obj:
                    MonthlySalesData.objects.filter(year=year, month=month).delete()
                continue
            # 存入数据库
            try:
                new_data = {
                    'year': year,
                    'month': month,
                    'turnover': turnover,
                    'operating_expenses': operating_expenses,
                    'amount_repaid': amount_repaid,
                    'inventory': inventory,
                    'profit': profit,
                }
                obj = MonthlySalesData.objects.filter(year=year, month=month)
                if obj:
                    # 如果该月数据已存在，则更新
                    MonthlySalesData.objects.filter(year=year, month=month).update(**new_data)
                    # print("%s年%s月 更新成功" % (year, month))
                else:
                    MonthlySalesData.objects.create(**new_data)
                    # print("%s年%s月 成功存入" % (year, month))
            except:
                # 删除所有数据
                MonthlySalesData.objects.filter(year=year).delete()
                continue