from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 登陆方法
    path('user_login/', views.user_login, name='user_login'),
    # 登出方法
    path('user_logout/', views.user_logout, name='user_logout'),
    # 展示账号管理页面方法
    path('user_management/', views.user_management, name='user_management'),
    # 新增账号方法
    path('add_user/', views.add_user, name='add_user'),
    # 删除用户方法
    path('delete_user/', views.delete_user, name='delete_user'),
    # 修改用户方法
    path('change_user/', views.change_user, name='change_user'),
    # 管理员修改账户密码方法
    path('admin_change_password/', views.admin_change_password, name='admin_change_password'),
    # 用户修改自己密码方法
    path('user_change_password/', views.user_change_password, name='user_change_password'),
    # 用户修改自己个人信息方法
    path('user_change_information/', views.user_change_information, name='user_change_information'),
    # 展示角色权限管理界面
    path('group_management/', views.group_management, name='group_management'),
    # 增加角色方法
    path('add_group/', views.add_group, name='add_group'),
    # 删除角色方法
    path('delete_group/', views.delete_group, name='delete_group'),
    # 修改角色方法
    path('change_group/', views.change_group, name='change_group'),
    # 从角色(组)批量赋予给账号方法
    path('group_to_user/', views.group_to_user, name='group_to_user'),

    # 展示月度营业数据方法
    path('show_monthly_sales_data/', views.show_monthly_sales_data, name='show_monthly_sales_data'),
    # 增加月度营业数据方法
    path('add_monthly_sales_data/', views.add_monthly_sales_data, name='add_monthly_sales_data'),
    # 删除月度营业数据方法
    path('delete_monthly_sales_data/', views.delete_monthly_sales_data, name='delete_monthly_sales_data'),
    # 修改月度营业数据方法
    path('change_monthly_sales_data/', views.change_monthly_sales_data, name='change_monthly_sales_data'),
    # 展示内控指标汇总表方法
    path('show_internal_control_indicators/', views.show_internal_control_indicators, name='show_internal_control_indicators'),
    # 增加内控指标汇总表方法
    path('add_internal_control_indicators/', views.add_internal_control_indicators, name='add_internal_control_indicators'),
    # 删除内控指标汇总表方法
    path('delete_internal_control_indicators/', views.delete_internal_control_indicators, name='delete_internal_control_indicators'),
    # 修改内控指标汇总方法
    path('change_internal_control_indicators/', views.change_internal_control_indicators, name='change_internal_control_indicators'),
    # 上传月度营业数据表格方法
    path('upload_monthly_performance/', views.upload_monthly_performance, name='upload_monthly_performance'),
    # 上传内控制表汇总表格方法
    path('upload_internal_control_indicators_performance/', views.upload_internal_control_indicators_performance, name='upload_internal_control_indicators_performance'),
    # 上传账号信息表方法
    path('upload_user/', views.upload_user, name='upload_user'),
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

    # 展示公式修改页-月度绩效考核
    path('month_result_formula/', views.month_result_formula, name='month_result_formula'),
    # 展示公式修改页-季度绩效考核
    path('quarter_result_formula/', views.quarter_result_formula, name='quarter_result_formula'),

    # 修改月度公式
    path('change_month_formula/', views.change_month_formula, name='change_month_formula'),
    # 修改季度公式
    path('change_quarter_formula/', views.change_quarter_formula, name='change_quarter_formula'),

    # 下载月度营业数据表格模板
    path('download_monthly_sales_modal/', views.download_monthly_sales_modal, name='download_monthly_sales_modal'),
    # 下载内控指标汇总模板
    path('download_internal_control_modal/', views.download_internal_control_modal, name='download_internal_control_modal'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page'),


]
