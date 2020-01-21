from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse('hello')


# 测试页面方法
def test_page(request):
    return render(request, 'performance/dark/月度营业数据.html')
