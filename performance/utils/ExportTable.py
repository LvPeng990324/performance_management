# 用于导出excel表格的动作

import xlwt
from io import BytesIO
from datetime import date
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from performance.models import MonthlySalesData
from performance.models import QuarterlySalesData
from performance.models import InternalControlIndicators
from performance.models import MonthlyPerformance
from performance.models import QuarterlyPerformance
from performance.models import QuarterlyAward
from performance.models import Logs


# 写入excel并生成下载回应方法
def excel_response(data_list, sheet_name):
    # 创建工作薄
    workbook = xlwt.Workbook(encoding='utf-8')
    # 创建工作表
    worksheet = workbook.add_sheet(sheet_name)
    # 设置日期样式
    date_style = xlwt.XFStyle()
    date_style.num_format_str = 'YYYY-MM-DD'

    # 遍历列表写入excel
    row_index = 0  # 行索引
    col_index = 0  # 列索引
    for line in data_list:
        for col_index in range(len(line)):
            # 获取要写入的数据
            data = line[col_index]
            # 写入一个单元格
            # 判断是不是datetime类型
            # 是的话就加日期样式写入
            if isinstance(data, date):
                # 是日期类型，加入样式
                worksheet.write(row_index, col_index, data, date_style)
            else:
                # 不是日期类型，直接写入
                worksheet.write(row_index, col_index, data)
        # 行索引自增
        row_index += 1
    # 生成下载回应
    sio = BytesIO()
    workbook.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(escape_uri_path(sheet_name))
    response.write(sio.getvalue())
    return response


# 导出月度营业数据
def export_monthly_sales_data():
    # 从数据库中取出所有数据
    data = MonthlySalesData.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['年份', '月份', '营业额', '营业费用', '回款额', '库存量', '利润额']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.year)
        temp_list.append(line.month)
        temp_list.append(line.turnover)
        temp_list.append(line.operating_expenses)
        temp_list.append(line.amount_repaid)
        temp_list.append(line.inventory)
        temp_list.append(line.profit)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='月度营业数据')


# 导出季度营业数据
def export_quarterly_sales_data():
    # 从数据库中取出所有数据
    data = QuarterlySalesData.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['年份', '季度', '营业额', '营业费用', '回款额', '库存量', '利润额']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.year)
        temp_list.append(line.quarter)
        temp_list.append(line.turnover)
        temp_list.append(line.operating_expenses)
        temp_list.append(line.amount_repaid)
        temp_list.append(line.inventory)
        temp_list.append(line.profit)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='季度营业数据')


# 导出内控指标汇总
def export_internal_control_indicators():
    # 从数据库中取出所有数据
    data = InternalControlIndicators.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['订单时间', '订单号', '订单额', '计划交期', '目标成品率', '目标医药费(万元)', '目标综合成本(万元)', '目标管理符合数',
                 '实际交期', '完成数', '未完成数', '实际成品率', '实际医药费', '实际成本', '实际管理符合数']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.order_date)  # 订单时间
        temp_list.append(line.order_number)  # 订单号
        temp_list.append(line.order_money)  # 订单额
        temp_list.append(line.scheduled_delivery)  # 计划交期
        temp_list.append(line.target_well_done_rate)  # 目标成品率
        temp_list.append(line.target_medical_expenses)  # 目标医药费
        temp_list.append(line.target_comprehensive_cost)  # 目标综合成本
        temp_list.append(line.target_management_compliance)  # 目标管理符合数
        # 一下为二次录入数据
        temp_list.append(line.actual_delivery)  # 实际交期
        temp_list.append(line.finished_number)  # 完成数
        temp_list.append(line.unfinished_number)  # 未完成数
        temp_list.append(line.actual_well_done_rate)  # 实际成品率
        temp_list.append(line.actual_medical_expenses)  # 实际医药费
        temp_list.append(line.actual_cost)  # 实际成本
        temp_list.append(line.actual_management_compliance)  # 实际管理符合数
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='内控指标汇总')


# 导出月度绩效考核结果
def export_monthly_performance():
    # 从数据库中取出所有数据
    data = MonthlyPerformance.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['年份', '月份', '交付率', '成品率', '医药费', '当月挖掘成本', '现场管理符合率']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.year)
        temp_list.append(line.month)
        temp_list.append(line.delivery_rate)
        temp_list.append(line.well_done_rate)
        temp_list.append(line.medical_expenses)
        temp_list.append(line.month_dig_cost)
        temp_list.append(line.field_management_well_rate)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='月度绩效考核结果')


# 导出季度绩效考核结果
def export_quarterly_performance():
    # 从数据库中取出所有数据
    data = QuarterlyPerformance.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['年份', '季度', '营业额', '营业费率', '回款额', '库存率', '利润率']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.year)
        temp_list.append(line.quarter)
        temp_list.append(line.turnover)
        temp_list.append(line.operating_rate)
        temp_list.append(line.repaid_rate)
        temp_list.append(line.inventory_rate)
        temp_list.append(line.profit_rate)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='季度绩效考核结果')


# 导出季度绩效奖金
# 导出季度绩效考核结果
def export_quarterly_award():
    # 从数据库中取出所有数据
    data = QuarterlyAward.objects.all()
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['年份', '季度', '营业额所得奖金额', '营业费率所得奖金额', 
                 '回款率所得奖金额', '库存率所得奖金额', '利润率所得奖金额', '合计']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.year)
        temp_list.append(line.quarter)
        temp_list.append(line.turnover_award)
        temp_list.append(line.operating_rate_award)
        temp_list.append(line.repaid_rate_award)
        temp_list.append(line.inventory_rate_award)
        temp_list.append(line.profit_rate_award)
        temp_list.append(line.total)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='季度绩效奖金')


# 导出用户操作日志
def export_user_logs():
    # 从数据库中取出所有数据
    data = Logs.objects.all().order_by('-log_time')
    # 将数据存入列表
    data_list = []  # 用于存储所有数据
    temp_list = []  # 用于临时存储一行，最后存入data_list
    # 建立表头
    temp_list = ['日志时间', '用户姓名', '工号', '动作描述', '操作结果']
    data_list.append(temp_list)
    temp_list = []
    # 遍历数据库内容并存入data_list
    for line in data:
        temp_list.append(line.log_time)
        temp_list.append(line.user_name)
        temp_list.append(line.job_number)
        temp_list.append(line.action)
        temp_list.append(line.result)
        # 存入data_list并清空temp_list
        data_list.append(temp_list)
        temp_list = []
    # 返回下载回应
    return excel_response(data_list, sheet_name='用户操作日志')
