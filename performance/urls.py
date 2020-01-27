from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 展示月度营业数据方法
    path('show_monthly_sales_data/', views.show_monthly_sales_data, name='show_monthly_sales_data'),
    # 增加月度营业数据方法
    path('add_monthly_sales_data/', views.add_monthly_sales_data, name='add_monthly_sales_data'),
    # 展示季度营业数据方法
    path('show_quarterly_sales_data/', views.show_quarterly_sales_data, name='show_quarterly_sales_data'),
    # 展示内控指标汇总表方法
    path('show_internal_control_indicators/', views.show_internal_control_indicators, name='show_internal_control_indicators'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page')
]
