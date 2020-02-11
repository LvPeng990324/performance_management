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

    # 展示管理层月度绩效考核结果方法
    path('show_monthly_result/', views.show_monthly_result, name='show_monthly_result'),
    # 刷新管理层月度绩效考核结果（更新数据库）方法
    path('refresh_monthly_result/', views.refresh_monthly_result, name='refresh_monthly_result'),
    # 展示管理层季度绩效考核结果方法
    path('show_quarterly_result/', views.show_quarterly_result, name='show_quarterly_result'),
    # 刷新管理层季度绩效考核结果（更新数据库）方法
    path('refresh_quarterly_result/', views.refresh_quarterly_result, name='refresh_quarterly_result'),

    # 仅展示月度营业数据方法
    path('display_monthly_sales_data/', views.display_monthly_sales_data, name='display_monthly_sales_data'),
    # 仅展示季度营业数据方法
    path('display_quarterly_sales_data/', views.display_quarterly_sales_data, name='display_quarterly_sales_data'),
    # 仅展示内控指标汇总方法
    path('display_internal_control_indicators/', views.display_internal_control_indicators, name='display_internal_control_indicators'),

    # 导出月度营业数据excel
    path('export_monthly_sales_data/', views.export_monthly_sales_data, name='export_monthly_sales_data'),
    # 导出季度营业数据excel
    path('export_quarterly_sales_data/', views.export_quarterly_sales_data, name='export_quarterly_sales_data'),
    # 导出内控指标汇总excel
    path('export_internal_control_indicators/', views.export_internal_control_indicators, name='export_internal_control_indicators'),
    # 导出月度绩效考核结果
    path('export_monthly_performance/', views.export_monthly_performance, name='export_monthly_performance'),
    # 导出季度绩效考核结果
    path('export_quarterly_performance/', views.export_quarterly_performance, name='export_quarterly_performance'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page')
    # 测试扩展用户表
    path('test_extension/', views.test_extension, name='test_extension'),
    # 测试用户登录验证
    path('test_authenticate/', views.test_authenticate, name='test_authenticate'),

]
