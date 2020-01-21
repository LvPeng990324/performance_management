from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 测试页面
    path('test_page/', views.test_page, name='test_page')
]
