from django.shortcuts import render, HttpResponse, redirect
from .models import MonthlySalesData
from .models import QuarterlySalesData
from .models import InternalControlIndicators
from datetime import datetime


def index(request):
    return HttpResponse('hello')


# 测试页面方法
def test_page(request):
    return render(request, 'performance/dark/月度营业数据.html')


# 展示月度营业数据方法
def show_monthly_sales_data(request):
    # 从数据库中取出所有数据
    monthly_sales_data = MonthlySalesData.objects.all()
    # 打包数据
    context = {
        'monthly_sales_data': monthly_sales_data,
    }
    # 引导前端页面
    return render(request, 'performance/dark/月度营业数据.html', context=context)


# 增加月度营业数据方法
def add_monthly_sales_data(request):
    # 从前端获取数据
    date_month = int(request.POST.get('date_month'))
    turnover = request.POST.get('turnover')
    operating_expenses = request.POST.get('operating_expenses')
    amount_repaid = request.POST.get('amount_repaid')
    inventory = request.POST.get('inventory')
    profit = request.POST.get('profit')

    # 转换日期对象
    date = datetime(year=1, month=date_month, day=1, hour=1, minute=1, second=1)

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
    delete_id = request.POST.get('delete_id')

    # 从数据库中删除
    MonthlySalesData.objects.get(id=delete_id).delete()

    # 重定向展示页面
    return redirect('show_monthly_sales_data')


# 修改月度营业数据
def change_monthly_sales_data(request):
    # 从前端获取要修改的id
    change_id = request.POST.get('change_id')
    # 从前端获取修改后的数据
    # change_date_month = int(request.POST.get('change_date_month'))
    change_turnover = request.POST.get('change_turnover')
    change_operating_expenses = request.POST.get('change_operating_expenses')
    change_amount_repaid = request.POST.get('change_amount_repaid')
    change_inventory = request.POST.get('change_inventory')
    change_profit = request.POST.get('change_profit')

    # 转换日期对象
    # change_date = datetime(year=1, month=change_date_month, day=1, hour=1, minute=1, second=1)

    # 从数据库中取出该数据
    data = MonthlySalesData.objects.get(id=change_id)
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
    return render(request, 'performance/dark/季度营业数据.html', context=context)


# 增加季度营业数据方法
def add_quarterly_sales_data(request):
    # 从前端获取数据
    quarterly = int(request.POST.get('quarterly'))
    turnover = request.POST.get('turnover')
    operating_expenses = request.POST.get('operating_expenses')
    amount_repaid = request.POST.get('amount_repaid')
    inventory = request.POST.get('inventory')
    profit = request.POST.get('profit')

    # 写入数据库
    QuarterlySalesData.objects.create(
        quarterly=quarterly,
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
    delete_id = request.POST.get('delete_id')

    # 从数据库中删除
    QuarterlySalesData.objects.get(id=delete_id).delete()

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
    return render(request, 'performance/dark/内控指标汇总表.html', context=context)


# 增加内控指标汇总表方法
def add_internal_control_indicators(request):
    # 从前端获取数据
    id = request.POST.get('id')
    date = request.POST.get('date')
    order_number = request.POST.get('order_number')
    plan_to_pay = request.POST.get('plan_to_pay')
    actual_payment = request.POST.get('actual_payment')
    finished_number = request.POST.get('finished_number')
    unfinished_number = request.POST.get('unfinished_number')
    target_well_done_rate = request.POST.get('target_well_done_rate')
    actual_well_done_rate = request.POST.get('actual_well_done_rate')
    month_medical_expenses = request.POST.get('month_medical_expenses')
    cost_per_wan = request.POST.get('cost_per_wan')
    field_management_compliance = request.POST.get('field_management_compliance')

    # 转换日期对象
    date_list = date.split('-')
    date = datetime(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]), hour=1, minute=1, second=1)

    # 存入数据库
    InternalControlIndicators.objects.create(
        id=id,
        date=date,
        order_number=order_number,
        plan_to_pay=plan_to_pay,
        actual_payment=actual_payment,
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
    delete_id = request.POST.get('delete_id')

    # 从数据库中删除
    InternalControlIndicators.objects.get(id=delete_id).delete()

    # 重定向展示页面
    return redirect('show_internal_control_indicators')
