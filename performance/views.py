from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .models import MonthlySalesData
from .models import QuarterlySalesData
from .models import InternalControlIndicators
from datetime import datetime
from .utils import UploadTable


def index(request):
    return render(request, '首页.html')


# 测试页面方法
def test_page(request):
    return render(request, '业务数据管理-月度营业数据.html')


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
    year = int(request.POST.get('year'))
    month = int(request.POST.get('month'))
    turnover = request.POST.get('turnover')
    operating_expenses = request.POST.get('operating_expenses')
    amount_repaid = request.POST.get('amount_repaid')
    inventory = request.POST.get('inventory')
    profit = request.POST.get('profit')

    # 转换日期对象
    date = datetime(year=year, month=month, day=1, hour=1, minute=1, second=1)

    # 写入数据库
    MonthlySalesData.objects.create(
        date=date,
        turnover=turnover,
        operating_expenses=operating_expenses,
        amount_repaid=amount_repaid,
        inventory=inventory,
        profit=profit,
    )

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 删除月度营业数据方法
def delete_monthly_sales_data(request):
    # 从前端获取要删除的id
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
    else:
        delete_id = request.POST.getlist('delete_id', [])

    # 从数据库中删除
    for id in delete_id:
        MonthlySalesData.objects.get(id=id).delete()

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 修改月度营业数据
def change_monthly_sales_data(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    # change_date_month = int(request.POST.get('change_date_month'))
    change_year = int(request.POST.get('change_year'))
    change_month = int(request.POST.get('change_month'))
    change_turnover = request.POST.get('change_turnover')
    change_operating_expenses = request.POST.get('change_operating_expenses')
    change_amount_repaid = request.POST.get('change_amount_repaid')
    change_inventory = request.POST.get('change_inventory')
    change_profit = request.POST.get('change_profit')

    # 转换日期对象
    change_date = datetime(year=change_year, month=change_month, day=1, hour=1, minute=1, second=1)

    # 从数据库中取出该数据
    data = MonthlySalesData.objects.get(id=change_id)
    # 修改数据
    data.date = change_date
    data.turnover = change_turnover
    data.operating_expenses = change_operating_expenses
    data.amount_repaid = change_amount_repaid
    data.inventory = change_inventory
    data.profit = change_profit
    # 保存更改
    data.save()

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

    # 重定向展示页面
    return redirect('show_quarterly_sales_data')


# 删除季度营业数据方法
def delete_quarterly_sales_data(request):
    # 从前端获取要删除的id
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
    else:
        delete_id = request.POST.getlist('delete_id', [])

    # 从数据库中删除
    for id in delete_id:
        QuarterlySalesData.objects.get(id=id).delete()

    # 重定向展示页面
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
    scheduled_delivery = datetime(year=int(scheduled_delivery_list[0]), month=int(scheduled_delivery_list[1]), day=int(scheduled_delivery_list[2]), hour=1, minute=1, second=1)
    actual_delivery = datetime(year=int(actual_delivery_list[0]), month=int(actual_delivery_list[1]), day=int(actual_delivery_list[2]), hour=1, minute=1, second=1)

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

    # 重定向展示页面
    return redirect('show_internal_control_indicators')


# 删除内控指标汇总表方法
def delete_internal_control_indicators(request):
    # 从前端获取要删除的id
    if request.method == 'GET':
        delete_id = request.GET.getlist('delete_id', [])
    else:
        delete_id = request.POST.getlist('delete_id', [])

    # 从数据库中删除
    for id in delete_id:
        InternalControlIndicators.objects.get(id=id).delete()

    # 重定向展示页面
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
    change_date = datetime(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]), hour=1, minute=1, second=1)
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
            # return HttpResponse('success')
            return redirect('show_monthly_sales_data')
        else:
            # return HttpResponse(result)
            return redirect('show_monthly_sales_data')


# 上传季度营业数据表格方法
def upload_quarterly_performance(request):
    if request.method == 'GET':
        return render(request, 'test_upload.html')
    else:
        file_data = request.FILES.get('upload_file')
        result = UploadTable.upload_quarterly_performance(file_data)
        if result == 0:
            # return HttpResponse('success')
            return redirect('show_quarterly_sales_data')
        else:
            # return HttpResponse(result)
            return redirect('show_quarterly_sales_data')


# 上传内控制表汇总表格方法
def upload_internal_control_indicators_performance(request):
    if request.method == 'GET':
        return render(request, 'test_upload.html')
    else:
        file_data = request.FILES.get('upload_file')
        result = UploadTable.upload_internal_control_indicators_performance(file_data)
        if result == 0:
            # return HttpResponse('success')
            return redirect('show_internal_control_indicators')
        else:
            # return HttpResponse(result)
            return redirect('show_internal_control_indicators')
