from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import MonthlySalesData
from .models import QuarterlySalesData
from .models import InternalControlIndicators
from .models import ConstantData
from .models import MonthlyPerformance
from .models import QuarterlyPerformance
from datetime import datetime
from .utils import UploadTable
from .utils import ExportTable
from .utils import CalcuteMonthlyPerformance
from .utils import CalculateQuarterlyPerformance


def index(request):
    return render(request, '首页.html')


# 测试页面方法
def test_page(request):
    return render(request, '数据统计-月度营业数据.html')


# 展示月度营业数据方法
def show_monthly_sales_data(request):
    # 从数据库中取出所有数据
    monthly_sales_data = MonthlySalesData.objects.all()
    # 打包数据
    context = {
        'monthly_sales_data': monthly_sales_data,
    }
    # 引导前端页面
    return render(request, '业务数据管理-月度营业数据.html', context=context)


# 增加月度营业数据方法
def add_monthly_sales_data(request):
    # 从前端获取数据
    year = request.POST.get('year')
    month = request.POST.get('month')
    turnover = request.POST.get('turnover')
    operating_expenses = request.POST.get('operating_expenses')
    amount_repaid = request.POST.get('amount_repaid')
    inventory = request.POST.get('inventory')
    profit = request.POST.get('profit')

    # 转换日期对象
    # date = datetime(year=year, month=month, day=1, hour=1, minute=1, second=1)

    # 写入数据库
    MonthlySalesData.objects.create(
        year=year,
        month=month,
        turnover=turnover,
        operating_expenses=operating_expenses,
        amount_repaid=amount_repaid,
        inventory=inventory,
        profit=profit,
    )

    # 写入成功提示
    messages.success(request, '数据添加成功')

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 删除月度营业数据方法
def delete_monthly_sales_data(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            MonthlySalesData.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中数据删除成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        MonthlySalesData.objects.get(id=delete_id).delete()
        # 写入删除成功提示
        messages.success(request, '数据删除成功')
        # 重载页面
        return redirect('show_monthly_sales_data')


# 修改月度营业数据
def change_monthly_sales_data(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    # change_date_month = int(request.POST.get('change_date_month'))
    change_year = request.POST.get('change_year')
    change_month = request.POST.get('change_month')
    change_turnover = request.POST.get('change_turnover')
    change_operating_expenses = request.POST.get('change_operating_expenses')
    change_amount_repaid = request.POST.get('change_amount_repaid')
    change_inventory = request.POST.get('change_inventory')
    change_profit = request.POST.get('change_profit')

    # 转换日期对象
    # change_date = datetime(year=change_year, month=change_month, day=1, hour=1, minute=1, second=1)

    # 从数据库中取出该数据
    data = MonthlySalesData.objects.get(id=change_id)
    # 修改数据
    data.year = change_year
    data.month = change_month
    data.turnover = change_turnover
    data.operating_expenses = change_operating_expenses
    data.amount_repaid = change_amount_repaid
    data.inventory = change_inventory
    data.profit = change_profit
    # 保存更改
    data.save()

    # 写入数据修改成功
    messages.success(request, '数据修改成功')

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 展示季度营业数据方法
def show_quarterly_sales_data(request):
    # 从数据库中取出所有数据
    quarterly_sales_data = QuarterlySalesData.objects.all()
    # 打包数据
    context = {
        'quarterly_sales_data': quarterly_sales_data,
    }
    # 引导前端页面
    return render(request, '业务数据管理-季度营业数据.html', context=context)


# 增加季度营业数据方法
def add_quarterly_sales_data(request):
    # 从前端获取数据
    year = int(request.POST.get('year'))
    quarter = int(request.POST.get('quarter'))
    turnover = request.POST.get('turnover')
    operating_expenses = request.POST.get('operating_expenses')
    amount_repaid = request.POST.get('amount_repaid')
    inventory = request.POST.get('inventory')
    profit = request.POST.get('profit')

    # 写入数据库
    QuarterlySalesData.objects.create(
        year=year,
        quarter=quarter,
        turnover=turnover,
        operating_expenses=operating_expenses,
        amount_repaid=amount_repaid,
        inventory=inventory,
        profit=profit,
    )

    # 写入成功提示
    messages.success(request, '数据增加成功')

    # 重定向展示页面
    return redirect('show_quarterly_sales_data')


# 删除季度营业数据方法
def delete_quarterly_sales_data(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            QuarterlySalesData.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中数据删除成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        QuarterlySalesData.objects.get(id=delete_id).delete()
        # 写入数据删除成功提示
        messages.success(request, '数据删除成功')
        # 重载页面
        return redirect('show_quarterly_sales_data')


# 修改季度营业数据方法
def change_quarterly_sales_data(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    change_turnover = request.POST.get('turnover')
    change_operating_expenses = request.POST.get('operating_expenses')
    change_amount_repaid = request.POST.get('amount_repaid')
    change_inventory = request.POST.get('inventory')
    change_profit = request.POST.get('profit')

    # 从数据库中取出该数据
    data = QuarterlySalesData.objects.get(id=change_id)
    # 修改数据
    # data.date = change_date
    data.turnover = change_turnover
    data.operating_expenses = change_operating_expenses
    data.amount_repaid = change_amount_repaid
    data.inventory = change_inventory
    data.profit = change_profit
    # 保存更改
    data.save()

    # 写入修改成功提示
    messages.success(request, '数据修改成功')

    # 重定向展示页面
    return redirect('show_quarterly_sales_data')


# 展示内控指标汇总表方法
def show_internal_control_indicators(request):
    # 从数据库中取出所有数据
    internal_control_indicators = InternalControlIndicators.objects.all()
    # 打包数据
    context = {
        'internal_control_indicators': internal_control_indicators,
    }
    # 引导前端页面
    return render(request, '业务数据管理-内控指标汇总.html', context=context)


# 增加内控指标汇总表方法
def add_internal_control_indicators(request):
    # 从前端获取数据
    id = request.POST.get('id')
    date = request.POST.get('date')
    order_number = request.POST.get('order_number')
    scheduled_delivery = request.POST.get('scheduled_delivery')
    actual_delivery = request.POST.get('actual_delivery')
    finished_number = request.POST.get('finished_number')
    unfinished_number = request.POST.get('unfinished_number')
    target_well_done_rate = request.POST.get('target_well_done_rate')
    actual_well_done_rate = request.POST.get('actual_well_done_rate')
    month_medical_expenses = request.POST.get('month_medical_expenses')
    cost_per_wan = request.POST.get('cost_per_wan')
    field_management_compliance = request.POST.get('field_management_compliance')

    # 转换日期对象
    date_list = date.split('-')
    scheduled_delivery_list = scheduled_delivery.split('-')
    actual_delivery_list = actual_delivery.split('-')
    date = datetime(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]), hour=1, minute=1, second=1)
    scheduled_delivery = datetime(year=int(scheduled_delivery_list[0]), month=int(scheduled_delivery_list[1]),
                                  day=int(scheduled_delivery_list[2]), hour=1, minute=1, second=1)
    actual_delivery = datetime(year=int(actual_delivery_list[0]), month=int(actual_delivery_list[1]),
                               day=int(actual_delivery_list[2]), hour=1, minute=1, second=1)

    # 存入数据库
    InternalControlIndicators.objects.create(
        id=id,
        date=date,
        order_number=order_number,
        scheduled_delivery=scheduled_delivery,
        actual_delivery=actual_delivery,
        finished_number=finished_number,
        unfinished_number=unfinished_number,
        target_well_done_rate=target_well_done_rate,
        actual_well_done_rate=actual_well_done_rate,
        month_medical_expenses=month_medical_expenses,
        cost_per_wan=cost_per_wan,
        field_management_compliance=field_management_compliance,
    )

    # 写入数据增加成功提示
    messages.success(request, '数据增加成功')

    # 重定向展示页面
    return redirect('show_internal_control_indicators')


# 删除内控指标汇总表方法
def delete_internal_control_indicators(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            InternalControlIndicators.objects.get(id=id).delete()
        # 写入数据删除成功提示
        messages.success(request, '选中数据删除成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        InternalControlIndicators.objects.get(id=delete_id).delete()
        # 写入数据删除成功提示
        messages.success(request, '数据删除成功')
        # 重载页面
        return redirect('show_internal_control_indicators')


# 修改内控指标汇总表方法
def change_internal_control_indicators(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    change_date = request.POST.get('date')
    change_order_number = request.POST.get('order_number')
    change_scheduled_delivery = request.POST.get('scheduled_delivery')
    change_actual_delivery = request.POST.get('actual_delivery')
    change_finished_number = request.POST.get('finished_number')
    change_unfinished_number = request.POST.get('unfinished_number')
    change_target_well_done_rate = request.POST.get('target_well_done_rate')
    change_actual_well_done_rate = request.POST.get('actual_well_done_rate')
    change_month_medical_expenses = request.POST.get('month_medical_expenses')
    change_cost_per_wan = request.POST.get('cost_per_wan')
    change_field_management_compliance = request.POST.get('field_management_compliance')

    # 转换日期对象
    date_list = change_date.split('-')
    scheduled_delivery_list = change_scheduled_delivery.split('-')
    actual_delivery_list = change_actual_delivery.split('-')
    change_date = datetime(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]), hour=1, minute=1,
                           second=1)
    change_scheduled_delivery = datetime(year=int(scheduled_delivery_list[0]), month=int(scheduled_delivery_list[1]),
                                         day=int(scheduled_delivery_list[2]), hour=1, minute=1, second=1)
    change_actual_delivery = datetime(year=int(actual_delivery_list[0]), month=int(actual_delivery_list[1]),
                                      day=int(actual_delivery_list[2]), hour=1, minute=1, second=1)

    # 从数据库中取出该数据
    data = InternalControlIndicators.objects.get(id=change_id)
    # 修改数据
    data.date = change_date
    data.order_number = change_order_number
    data.scheduled_delivery = change_scheduled_delivery
    data.actual_delivery = change_actual_delivery
    data.finished_number = change_finished_number
    data.unfinished_number = change_unfinished_number
    data.target_well_done_rate = change_target_well_done_rate
    data.actual_well_done_rate = change_actual_well_done_rate
    data.month_medical_expenses = change_month_medical_expenses
    data.cost_per_wan = change_cost_per_wan
    data.field_management_compliance = change_field_management_compliance
    # 保存更改
    data.save()

    # 返回数据修改成功提示
    messages.success(request, '数据修改成功')

    # 重定向展示页面
    return redirect('show_internal_control_indicators')


# 传递月度营业数据接口方法
def give_monthly_sales_data(request):
    # 从数据库中取出所有数据
    data = MonthlySalesData.objects.values()
    return JsonResponse(list(data), safe=False)


# 传递季度营业数据接口方法
def give_quarterly_sales_data(request):
    # 从数据库中取出所有数据
    data = QuarterlySalesData.objects.values()
    return JsonResponse(list(data), safe=False)


# 传递内控制表汇总接口方法
def give_internal_control_indicators(request):
    # 从数据库中取出所有数据
    data = InternalControlIndicators.objects.values()
    return JsonResponse(list(data), safe=False)


# 上传月度营业数据表格方法
def upload_monthly_performance(request):
    if request.method == 'GET':
        return render(request, 'test_upload.html')
    else:
        file_data = request.FILES.get('upload_file')
        result = UploadTable.upload_monthly_performance(file_data)
        if result == 0:
            # 写入导入成功提示
            messages.success(request, '导入成功')
            # 重定向数据展示页面
            return redirect('show_monthly_sales_data')
        else:
            # 写入相应的错误提示
            messages.error(request, result)
            # 重定向数据展示页面
            return redirect('show_monthly_sales_data')


# 上传季度营业数据表格方法
def upload_quarterly_performance(request):
    if request.method == 'GET':
        return render(request, 'test_upload.html')
    else:
        file_data = request.FILES.get('upload_file')
        result = UploadTable.upload_quarterly_performance(file_data)
        if result == 0:
            # 写入导入成功提示
            messages.success(request, '导入成功')
            # 重定向数据展示页面
            return redirect('show_quarterly_sales_data')
        else:
            # 写入相应的错误提示
            messages.error(request, result)
            # 重定向数据展示页面
            return redirect('show_quarterly_sales_data')


# 上传内控制表汇总表格方法
def upload_internal_control_indicators_performance(request):
    if request.method == 'GET':
        return render(request, 'test_upload.html')
    else:
        file_data = request.FILES.get('upload_file')
        result = UploadTable.upload_internal_control_indicators_performance(file_data)
        if result == 0:
            # 写入导入成功提示
            messages.success(request, '导入成功')
            # 重定向数据展示页面
            return redirect('show_internal_control_indicators')
        else:
            # 写入相应的错误提示
            messages.error(request, result)
            # 重定向数据展示页面
            return redirect('show_internal_control_indicators')


# 展示常量数据方法
def show_constant_data(request):
    # 从数据库中取出所有数据
    constant_data = ConstantData.objects.all()
    # 打包数据
    context = {
        'constant_data': constant_data,
    }
    # 引导前端页面
    return render(request, '常量数据.html', context=context)


# 增加常量数据方法
def add_constant_data(request):
    # 从前端获取数据
    date = request.POST.get('date')
    month_plan_order_number = request.POST.get('month_plan_order_number')
    target_cost = request.POST.get('target_cost')
    field_management_compliance_target_number = request.POST.get('field_management_compliance_target_number')
    annual_target_turnover = request.POST.get('annual_target_turnover')
    annual_target_award = request.POST.get('annual_target_award')

    # 转换日期对象
    date_list = date.split('-')
    date = datetime(year=int(date_list[0]), month=int(date_list[1]), day=1, hour=1, minute=1, second=1)

    # 写入数据库
    ConstantData.objects.create(
        date=date,
        month_plan_order_number=month_plan_order_number,
        target_cost=target_cost,
        field_management_compliance_target_number=field_management_compliance_target_number,
        annual_target_turnover=annual_target_turnover,
        annual_target_award=annual_target_award,
    )

    # 写入成功提示
    messages.success(request, '数据添加成功')

    # 重定向展示页面
    return redirect('show_constant_data')


# 删除常量数据方法
def delete_constant_data(request):
    # get为多选删除，post为单条删除
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
        # 遍历删除
        for id in delete_id:
            ConstantData.objects.get(id=id).delete()
        # 写入删除成功提示
        messages.success(request, '选中数据删除成功')
        # 返回成功
        return HttpResponse('success')
    else:
        delete_id = request.POST.get('delete_id')
        # 从数据库中删除
        ConstantData.objects.get(id=delete_id).delete()
        # 写入删除成功提示
        messages.success(request, '数据删除成功')
        # 重载页面
        return redirect('show_constant_data')


# 修改常量数据方法
def change_constant_data(request):
    pass


# 上传常量数据表格方法
def upload_constant_data(request):
    file_data = request.FILES.get('upload_file')
    result = UploadTable.upload_constant_data(file_data)
    if result == 0:
        # 写入导入成功提示
        messages.success(request, '导入成功')
        # 重定向数据展示页面
        return redirect('show_constant_data')
    else:
        # 写入相应的错误提示
        messages.error(request, result)
        # 重定向数据展示页面
        return redirect('show_constant_data')


# 展示管理层月度绩效考核结果方法
def show_monthly_result(request):
    # 从数据库中取出所有数据
    monthly_result = MonthlyPerformance.objects.all()
    # 打包数据
    context = {
        'monthly_result': monthly_result,
    }
    # 引导前端页面
    return render(request, '数据统计-管理层月度绩效考核结果.html', context=context)


# 更新月度绩效考核结果的数据
def refresh_monthly_result(request):
    # 更新月度绩效考核结果中数据项的值，并更新数据库
    result = CalcuteMonthlyPerformance.monthly_get_and_refresh()
    if result == 'success':
        messages.success(request, '数据刷新成功')
    else:
        messages.error(result, '数据刷新失败，请重试')
    return redirect('show_monthly_result')


# 展示管理层季度绩效考核结果方法
def show_quarterly_result(request):
    # 从数据库中取出所有数据
    quarterly_result = QuarterlyPerformance.objects.all()
    # 打包数据
    context = {
        'quarterly_result': quarterly_result,
    }
    # 引导前端页面
    return render(request, '数据统计-季度绩效考核结果.html', context=context)


# 更新季度绩效考核结果的数据
def refresh_quarterly_result(request):
    # 更新季度绩效考核结果中数据项的值，并更新数据库
    result = CalculateQuarterlyPerformance.quarterly_get_and_refresh()
    if result == 'success':
        messages.success(request, '数据刷新成功')
    else:
        messages.error(result, '数据刷新失败，请重试')
    return redirect('show_quarterly_result')


# 仅展示月度营业数据方法
def display_monthly_sales_data(request):
    # 从数据库中取出所有数据
    monthly_sales_data = MonthlySalesData.objects.all()
    # 打包数据
    context = {
        'monthly_sales_data': monthly_sales_data,
    }
    # 引导前端页面
    return render(request, '数据统计-月度营业数据.html', context=context)


# 仅展示季度营业数据方法
def display_quarterly_sales_data(request):
    # 从数据库中取出所有数据
    quarterly_sales_data = QuarterlySalesData.objects.all()
    # 打包数据
    context = {
        'quarterly_sales_data': quarterly_sales_data,
    }
    # 引导前端页面
    return render(request, '数据统计-季度营业数据.html', context=context)


# 仅展示内控指标汇总方法
def display_internal_control_indicators(request):
    # 从数据库中取出所有数据
    internal_control_indicators = InternalControlIndicators.objects.all()
    # 打包数据
    context = {
        'internal_control_indicators': internal_control_indicators,
    }
    # 引导前端页面
    return render(request, '数据统计-内控指标汇总.html', context=context)


# 导出月度营业数据excel
def export_monthly_sales_data(request):
    return ExportTable.export_monthly_sales_data()


# 导出季度营业数据excel
def export_quarterly_sales_data(request):
    return ExportTable.export_quarterly_sales_data()


# 导出内控指标汇总excel
def export_internal_control_indicators(request):
    return ExportTable.export_internal_control_indicators()


# 导出月度绩效考核结果
def export_monthly_performance(request):
    return ExportTable.export_monthly_performance()


# 导出季度绩效考核结果
def export_quarterly_performance(request):
    return ExportTable.export_quarterly_performance()
