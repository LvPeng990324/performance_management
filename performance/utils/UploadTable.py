# 用于处理上传excel、csv文件的动作
# 包含前三张表格的文件上传动作
# 参数传入文件对象
# 判断文件类型、读取、验证、写入数据库操作
# 一旦出了问题即返回错误信息

import xlrd
import csv
from datetime import datetime
from performance.models import MonthlySalesData
from performance.models import QuarterlySalesData
from performance.models import InternalControlIndicators
from performance.models import ConstantData
from performance.models import User


# 将excel中日期类型转为datetime对象
def to_datetime(data, xldate):
    # 转化为日期元组(2020, 2, 4, 0, 0, 0)，元素为int
    data_value = xlrd.xldate_as_tuple(xldate.value, data.datemode)
    # 转化为datetime对象
    dt_date = datetime(
        year=data_value[0],
        month=data_value[1],
        day=data_value[2],
        hour=data_value[3],
        minute=data_value[4],
        second=data_value[5],
    )
    # 返回datetime对象
    return dt_date


# 返回列表形式excel数据
def get_excel_list(file_data):
    # 解析excel
    data = xlrd.open_workbook(filename=None, file_contents=file_data.read())
    # 获取第一张表对象
    table = data.sheet_by_index(0)
    # 将数据写入列表
    table_list = []  # 存放所有表格数据
    temp_list = []  # 存放一行数据，然后写入table_list
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    # 双层遍历，忽略第一行表头
    for i in range(1, nrows):
        for j in range(ncols):
            cell_data = table.cell(i, j)
            # 判断是不是excel日期类型
            # 是的话就转化为datetime对象然后写入temp_list
            # 不是的话就直接写入temp_list
            # ctype说明：0 empty, 1 string, 2 number, 3 date, 4 boolean, 5 error
            if cell_data.ctype == 3:
                temp_list.append(to_datetime(data=data, xldate=cell_data))
            else:
                temp_list.append(cell_data.value)
        # 将temp_list写入到table_list并清空temp_list
        table_list.append(temp_list)
        temp_list = []
    # 释放内存
    data.release_resources()
    # 返回列表数据
    return table_list


# 返回表格形式csv数据
def get_csv_list(file_data):
    pass


# 判断文件类型
def get_file_type(file_data):
    # 返回文件后缀
    return str(file_data).split('.')[-1]


# 上传月度营业数据表
def upload_monthly_performance(file_data):
    # 判断文件类型并分别使用下边不同方法处理
    file_type = get_file_type(file_data)
    # excel表
    if file_type == 'xls' or file_type == 'xlsx':
        return upload_monthly_performance_excel(file_data)
    # csv表
    elif file_type == 'csv':
        return upload_monthly_performance_csv(file_data)
    # 不支持的类型返回错误信息
    else:
        return '不支持的文件类型'


# 月度营业数据excel表
def upload_monthly_performance_excel(file_data):
    # 获取列表数据
    table_list = get_excel_list(file_data)
    # 将数据写入数据库
    try:
        for temp_data in table_list:
            MonthlySalesData.objects.create(
                year=temp_data[0],
                month=temp_data[1],
                turnover=temp_data[2],
                operating_expenses=temp_data[3],
                amount_repaid=temp_data[4],
                inventory=temp_data[5],
                profit=temp_data[6],
            )
    except:
        return '写入数据库失败'
    return 0


# 月度营业数据csv表
def upload_monthly_performance_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'


# 上传季度营业数据表
def upload_quarterly_performance(file_data):
    # 判断文件类型并分别使用下边不同方法处理
    file_type = get_file_type(file_data)
    # excel表
    if file_type == 'xls' or file_type == 'xlsx':
        return upload_quarterly_performance_excel(file_data)
    # csv表
    elif file_type == 'csv':
        upload_quarterly_performance_csv(file_data)
    # 不支持的类型返回错误信息
    else:
        return '不支持的文件类型'


# 季度营业数据excel表
def upload_quarterly_performance_excel(file_data):
    # 获取列表数据
    table_list = get_excel_list(file_data)
    # 将数据写入数据库
    try:
        for temp_data in table_list:
            QuarterlySalesData.objects.create(
                year=temp_data[0],
                quarter=temp_data[1],
                turnover=temp_data[2],
                operating_expenses=temp_data[3],
                amount_repaid=temp_data[4],
                inventory=temp_data[5],
                profit=temp_data[6],
            )
    except:
        return '写入数据库失败'

    return 0


# 季度营业数据csv表
def upload_quarterly_performance_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'


# 上传内控指标汇总表
def upload_internal_control_indicators_performance(file_data):
    # 判断文件类型并分别使用下边不同方法处理
    file_type = get_file_type(file_data)
    # excel表
    if file_type == 'xls' or file_type == 'xlsx':
        return upload_internal_control_indicators_performance_excel(file_data)
    # csv表
    elif file_type == 'csv':
        upload_internal_control_indicators_performance_csv(file_data)
    # 不支持的类型返回错误信息
    else:
        return '不支持的文件类型'


# 内控指标汇总excel表
def upload_internal_control_indicators_performance_excel(file_data):
    # 获取列表数据
    table_list = get_excel_list(file_data)
    # 将数据写入数据库
    try:
        for temp_data in table_list:
            InternalControlIndicators.objects.create(
                date=temp_data[0],
                order_number=temp_data[1],
                scheduled_delivery=temp_data[2],
                actual_delivery=temp_data[3],
                finished_number=temp_data[4],
                unfinished_number=temp_data[5],
                target_well_done_rate=temp_data[6],
                actual_well_done_rate=temp_data[7],
                month_medical_expenses=temp_data[8],
                cost_per_wan=temp_data[9],
                field_management_compliance=temp_data[10],
            )
    except:
        return '写入数据库失败'
    return 0


# 内控指标汇总csv表
def upload_internal_control_indicators_performance_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'


# 上传常量数据表
def upload_constant_data(file_data):
    # 判断文件类型并分别使用下边不同方法处理
    file_type = get_file_type(file_data)
    # excel表
    if file_type == 'xls' or file_type == 'xlsx':
        return upload_constant_data_excel(file_data)
    # csv表
    elif file_type == 'csv':
        upload_constant_data_csv(file_data)
    # 不支持的类型返回错误信息
    else:
        return '不支持的文件类型'


# 常量数据excel表
def upload_constant_data_excel(file_data):
    # 获取列表数据
    table_list = get_excel_list(file_data)
    # 将数据写入数据库
    try:
        for temp_data in table_list:
            ConstantData.objects.create(
                date=temp_data[0],
                month_plan_order_number=temp_data[1],
                target_cost=temp_data[2],
                field_management_compliance_target_number=temp_data[3],
                annual_target_turnover=temp_data[4],
                annual_target_award=temp_data[5],
            )
    except:
        return '写入数据库失败'
    return 0


# 常量数据csv表
def upload_constant_data_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'


# 上传账号信息表
def upload_user(file_data):
    # 判断文件类型并分别使用下边不同方法处理
    file_type = get_file_type(file_data)
    # excel表
    if file_type == 'xls' or file_type == 'xlsx':
        return upload_user_excel(file_data)
    # csv表
    elif file_type == 'csv':
        upload_user_csv(file_data)
    # 不支持的类型返回错误信息
    else:
        return '不支持的文件类型'


# 账号信息excel表
def upload_user_excel(file_data):
    # 获取列表数据
    table_list = get_excel_list(file_data)
    # 将数据写入数据库
    try:
        for temp_data in table_list:
            user = User.objects.create_user(
                username=str(temp_data[1]),
                password=str(temp_data[4]),
                last_name=str(temp_data[2]),
            )
            user.extension.job_number = str(temp_data[1])
            user.extension.department = str(temp_data[0])
            user.extension.telephone = str(temp_data[3])
            user.save()
    except:
        return '写入数据库失败'
    return 0


# 账号信息csv表
def upload_user_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'
