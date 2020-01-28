from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 展示月度营业数据方法
    path('show_monthly_sales_data/', views.show_monthly_sales_data, name='show_monthly_sales_data'),
    # 增加月度营业数据方法
    path('add_monthly_sales_data/', views.add_monthly_sales_data, name='add_monthly_sales_data'),
    # 删除月度营业数据方法
    path('delete_monthly_sales_data', views.delete_monthly_sales_data, name='delete_monthly_sales_data'),
    # 展示季度营业数据方法
    path('show_quarterly_sales_data/', views.show_quarterly_sales_data, name='show_quarterly_sales_data'),
    # 增加季度营业数据方法
    path('add_quarterly_sales_data/', views.add_quarterly_sales_data, name='add_quarterly_sales_data'),
    # 删除季度营业数据方法
    path('delete_quarterly_sales_data', views.delete_quarterly_sales_data, name='delete_quarterly_sales_data'),
    # 展示内控指标汇总表方法
    path('show_internal_control_indicators/', views.show_internal_control_indicators, name='show_internal_control_indicators'),
    # 增加内控指标汇总表方法
    path('add_internal_control_indicators', views.add_internal_control_indicators, name='add_internal_control_indicators'),
    # 删除内控制表汇总表方法
    path('delete_internal_control_indicators', views.delete_internal_control_indicators, name='delete_internal_control_indicators'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page')
]
