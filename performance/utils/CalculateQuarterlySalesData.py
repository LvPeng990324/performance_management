# 根据月度营业数据来生成季度营业数据文件

import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'performance_management.settings')
django.setup()

from performance.models import MonthlySalesData
from performance.models import QuarterlySalesData
from django.db.models import Sum


def quarterly_data_production(year, year_res_set, quarter_list):
    """
    创建季度数据并存入数据库
    PS.消息队列可能需要依赖返回值
    :param year: 年份
    :param year_res_set: 全年数据
    :param quarter_list: 季度列表（{(1,2,3),(4,5,6),(7,,8,9),(10,11,12)}）
    """
    if 1 in quarter_list:
        quarter = 1
    if 4 in quarter_list:
        quarter = 2
    if 7 in quarter_list:
        quarter = 3
    if 10 in quarter_list:
        quarter = 4

    res = year_res_set.filter(month__in=quarter_list)
    if res.exists():
        # 月度表中存在数据
        res = res.aggregate(
            turnover_sum=Sum("turnover"),
            operating_expenses_sum=Sum("operating_expenses"),
            amount_repaid_sum=Sum("amount_repaid"),
            inventory_sum=Sum("inventory"),
            profit_sum=Sum("profit")
        )
        new_data = {
            'year': year,
            'quarter': quarter,
            'turnover': res['turnover_sum'],
            'operating_expenses': res['operating_expenses_sum'],
            'amount_repaid': res['amount_repaid_sum'],
            'inventory': res['inventory_sum'],
            'profit': res['profit_sum'],
        }
        obj = QuarterlySalesData.objects.filter(year=year, quarter=quarter)
        if obj.exists():
            # 如果该月数据已存在，则更新
            obj.update(**new_data)
            # print("%s年%s季 更新成功" % (year, quarter))
        else:
            QuarterlySalesData.objects.create(**new_data)
            # print("%s年%s季 成功存入" % (year, quarter))
    else:
        # 月度表中不存在数据
        # 同步删除季度表中的数据
        obj = QuarterlySalesData.objects.filter(year=year, quarter=quarter)
        if obj.exists():
            obj.delete()


def calculate_quarterly_sales_data(year=MonthlySalesData.objects.values_list('year', flat=True).distinct()):
    """
        功能：由月度数据生成季度数据
        参考：季度/月度字段
            year = models.IntegerField(verbose_name='年份')
            quarter = models.IntegerField(verbose_name='季度')
            turnover = models.FloatField(verbose_name='营业额')
            operating_expenses = models.FloatField(verbose_name='营业费用')
            amount_repaid = models.FloatField(verbose_name='回款额')
            inventory = models.FloatField(verbose_name='库存量')
            profit = models.FloatField(verbose_name='利润额')
    """

    success_message = ""
    error_message = ""
    for year_ in year:
        year_res_set = MonthlySalesData.objects.filter(year=year_)
        quarterly_data_production(year_, year_res_set, [1, 2, 3])
        quarterly_data_production(year_, year_res_set, [4, 5, 6])
        quarterly_data_production(year_, year_res_set, [7, 8, 9])
        quarterly_data_production(year_, year_res_set, [10, 11, 12])
