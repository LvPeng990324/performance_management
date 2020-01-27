from django.shortcuts import render, HttpResponse
from .models import MonthlySalesData
from .models import QuarterlySalesData
from .models import InternalControlIndicators


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
