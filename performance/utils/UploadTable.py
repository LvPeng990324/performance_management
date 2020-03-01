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
            elif cell_data.ctype == 2:
                temp_list.append(cell_data.value)
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
            # 将列表数据分类
            year = temp_data[0]
            month = temp_data[1]
            turnover = temp_data[2]
            operating_expenses = temp_data[3]
            amount_repaid = temp_data[4]
            inventory = temp_data[5]
            profit = float(temp_data[2]) - float(temp_data[3])
            MonthlySalesData.objects.create(
                year=year,
                month=month,
                turnover=turnover,
                operating_expenses=operating_expenses,
                amount_repaid=amount_repaid,
                inventory=inventory,
                profit=profit,
            )
    except:
        return '写入数据库失败'
    return str(len(table_list))


# 月度营业数据csv表
def upload_monthly_performance_csv(file_data):
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


    # try:
    for temp_data in table_list:

        # 整理列表数据
        order_date = temp_data[0]
        order_number = temp_data[1]
        order_money = temp_data[2]
        scheduled_delivery = temp_data[3]
        target_well_done_rate = temp_data[4]
        actual_delivery = temp_data[5]
        actual_well_done_rate = temp_data[6]
        actual_medical_expenses = temp_data[7]
        actual_cost = temp_data[8]
        actual_management_compliance = temp_data[9]

        # 从常量数据表中取出相应的常量数据
        # 规则为，日期在这条数据之前的最新一条常量数据
        # 获取符合条件的一批常量
        constant_data = ConstantData.objects.filter(date__lte=order_date).last()
        # 如果没获取到符合条件的常量，写入错误信息
        if not constant_data:
            return '未找到符合条件的常量数据，请检查订单时间或者联系管理员录入常量数据'
        # 获取常量数据
        target_medical_expenses_rate = constant_data.target_medical_expenses_rate  # 目标医药费百分比
        target_comprehensive_cost_rate = constant_data.target_comprehensive_cost_rate  # 目标综合成本百分比
        target_management_compliance_value = constant_data.target_management_compliance_value  # 目标管理符合数值
        # 计算数据项
        target_medical_expenses = float(order_money) * target_medical_expenses_rate  # 目标医药费
        target_comprehensive_cost = float(order_money) * target_comprehensive_cost_rate  # 目标综合成本
        target_management_compliance = float(order_money) * target_management_compliance_value  # 目标管理符合数
        # 比对实际交期于计划交期，生成完成数于未完成数
        # 实际交期在计划交期之前，完成数 = 1，未完成数 = 0
        # 实际交期在计划交期之后，完成数 = 0，未完成数 = 1
        if actual_delivery <= scheduled_delivery:
            # 按时完成
            finished_number = 1
            unfinished_number = 0
        else:
            # 未按时完成
            finished_number = 0
            unfinished_number = 1

        # 将数据写入数据库
        InternalControlIndicators.objects.create(
            order_date=order_date,
            order_number=order_number,
            order_money=order_money,
            scheduled_delivery=scheduled_delivery,
            target_well_done_rate=target_well_done_rate,
            target_medical_expenses=target_medical_expenses,
            target_comprehensive_cost=target_comprehensive_cost,
            target_management_compliance=target_management_compliance,
            actual_delivery=actual_delivery,
            finished_number=finished_number,
            unfinished_number=unfinished_number,
            actual_well_done_rate=actual_well_done_rate,
            actual_medical_expenses=actual_medical_expenses,
            actual_cost=actual_cost,
            actual_management_compliance=actual_management_compliance,
        )
    # except:
    #     return '写入数据库失败'
    return str(len(table_list))


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
    return str(len(table_list))


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
            # 将列表数据分类
            department = str(temp_data[0]).strip()
            job_number = str(temp_data[1]).split('.')[0]
            name = temp_data[2].strip()
            telephone = str(temp_data[3]).split('.')[0]
            password = temp_data[4].strip()
            user = User.objects.create_user(
                username=job_number,
                password=password,
                last_name=name,
            )
            user.extension.job_number = job_number
            user.extension.department = department
            user.extension.telephone = telephone
            user.save()
    except:
        return '写入数据库失败'
    return str(len(table_list))


# 账号信息csv表
def upload_user_csv(file_data):
    return '暂不支持csv文件，请先转换为excel'
