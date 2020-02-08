from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 展示月度营业数据方法
    path('show_monthly_sales_data/', views.show_monthly_sales_data, name='show_monthly_sales_data'),
    # 增加月度营业数据方法
    path('add_monthly_sales_data/', views.add_monthly_sales_data, name='add_monthly_sales_data'),
    # 删除月度营业数据方法
    path('delete_monthly_sales_data/', views.delete_monthly_sales_data, name='delete_monthly_sales_data'),
    # 修改月度营业数据方法
    path('change_monthly_sales_data/', views.change_monthly_sales_data, name='change_monthly_sales_data'),
    # 展示季度营业数据方法
    path('show_quarterly_sales_data/', views.show_quarterly_sales_data, name='show_quarterly_sales_data'),
    # 增加季度营业数据方法
    path('add_quarterly_sales_data/', views.add_quarterly_sales_data, name='add_quarterly_sales_data'),
    # 删除季度营业数据方法
    path('delete_quarterly_sales_data/', views.delete_quarterly_sales_data, name='delete_quarterly_sales_data'),
    # 修改季度营业数据方法
    path('change_quarterly_sales_data/', views.change_quarterly_sales_data, name='change_quarterly_sales_data'),
    # 展示内控指标汇总表方法
    path('show_internal_control_indicators/', views.show_internal_control_indicators, name='show_internal_control_indicators'),
    # 增加内控指标汇总表方法
    path('add_internal_control_indicators/', views.add_internal_control_indicators, name='add_internal_control_indicators'),
    # 删除内控指标汇总表方法
    path('delete_internal_control_indicators/', views.delete_internal_control_indicators, name='delete_internal_control_indicators'),
    # 修改内控指标汇总方法
    path('change_internal_control_indicators/', views.change_internal_control_indicators, name='change_internal_control_indicators'),
    # 传递月度营业数据接口方法
    path('give_monthly_sales_data/', views.give_monthly_sales_data, name='give_monthly_sales_data'),
    # 传递季度营业数据接口方法
    path('give_quarterly_sales_data/', views.give_quarterly_sales_data, name='give_quarterly_sales_data'),
    # 传递内控制表汇总接口方法
    path('give_internal_control_indicators/', views.give_internal_control_indicators, name='give_internal_control_indicators'),
    # 上传月度营业数据表格方法
    path('upload_monthly_performance/', views.upload_monthly_performance, name='upload_monthly_performance'),
    # 上传季度营业数据表格方法
    path('upload_quarterly_performance/', views.upload_quarterly_performance, name='upload_quarterly_performance'),
    # 上传内控制表汇总表格方法
    path('upload_internal_control_indicators_performance/', views.upload_internal_control_indicators_performance, name='upload_internal_control_indicators_performance'),
    # 增加常量数据方法
    path('add_constant_data/', views.add_constant_data, name='add_constant_data'),
    # 删除常量数据方法
    path('delete_constant_data/', views.delete_constant_data, name='delete_constant_data'),
    # 修改常量数据方法
    path('change_constant_data/', views.change_constant_data, name='change_constant_data'),
    # 上传常量数据表格方法
    path('upload_constant_data/', views.upload_constant_data, name='upload_constant_data'),
    # 展示常量数据方法
    path('show_constant_data/', views.show_constant_data, name='show_constant_data'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page')
]
